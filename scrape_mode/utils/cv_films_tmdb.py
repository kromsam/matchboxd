"""Add TMDB ids to a list of films"""
import re
import requests

from utils.db_utils import load_db_data
from utils.utils import load_string


def add_tmdb_id(db, api_key):
    """Add tmdb id to json file"""
    print("Loading films from database...")
    query = "SELECT * FROM films"
    films = load_db_data(db, query)
    print("Films loaded.")

    # Convert file to key
    api_key = load_string(api_key)

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
