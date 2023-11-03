"""Add TMDB ids to a list of films"""
import sqlite3
import re
import requests

from db_utils import db_conn
from utils import get_lb_list

def get_movie_id(movie_title, api_key):
    """Get tmdb id from movie title"""
    base_url = "https://api.themoviedb.org/3/search/movie"
    params = {
        "api_key": api_key,
        "query": movie_title
    }
    response = requests.get(base_url, params=params, timeout=20)
    tmdb_data = response.json()
    if tmdb_data.get('results'):
        return tmdb_data['results'][0]['id']
    return None


def load_cv_films(db):
    # Execute a SQL query to select films with lb_check=True
    conn = db_conn(db)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM films")

    # Fetch all the rows that match the condition
    film_data_raw = cursor.fetchall()
    conn.close()

    film_data = []
    for row in film_data_raw:
        film_dict = dict(row)
        film_data.append(film_dict)
    return film_data


def add_tmdb_id(db, api_key):
    """Add tmdb id to json file"""
    print(f"Loading films from database...")
    films = load_cv_films(db)
    print("Films loaded.")

    # Convert file to key
    api_key = get_lb_list(api_key)

    for film in films:
        movie_title = film["title"]
        print(f"Searching TMDB id for: {movie_title}.")
        movie_id = get_movie_id(movie_title, api_key)
        if movie_id is None:
            if '(' in movie_title or ')' in movie_title:
                print("Film not found, trying again without ().")
                # Define a regular expression pattern to remove text inside parentheses
                pattern = r'\([^)]*\)'

                # Use the re.sub() function to remove text inside parentheses
                cleaned_title = re.sub(pattern, '', movie_title)

                # Remove any trailing hyphens and extra spaces
                cleaned_title = cleaned_title.strip()
                cleaned_title = re.sub(r'-+$', '', cleaned_title)
                movie_id = get_movie_id(cleaned_title, api_key)
            if ':' in movie_title:
                print("Film not found, trying again removing everything after : .")
                cleaned_title = re.sub(r':.*', '', movie_title)
                cleaned_title.strip()
                movie_id = get_movie_id(cleaned_title, api_key)
                if movie_id is None:
                    print("Film not found, trying again removing everything before : .")
                    pattern = r':\s(.*)$'
                    cleaned_title = re.sub(pattern, ':', movie_title, flags=re.MULTILINE)
                    movie_id = get_movie_id(cleaned_title, api_key)
        if movie_id is None:
            print("Film not found.")
        film["tmdb_id"] = movie_id
        print(f"TMDB id for {movie_title}: {movie_id}.")
    return films
