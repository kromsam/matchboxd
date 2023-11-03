import sqlite3
import json

from db_utils import db_conn
from db_utils import db_close

from utils import store_data

def generate_json(db, output_file):
    conn = db_conn(db)
    cursor = conn.cursor()

    # Define the query to select films with lb_check is true
    query = """
    SELECT tmdb_id, title, url, screening_state, oneliner, img_url, imdb_id, lb_title, release_year, adult, lb_url
    FROM films
    WHERE lb_check = 1
    """

    # Execute the query and fetch the results
    cursor.execute(query)
    film_rows = cursor.fetchall()

    # Create a list to store the film data
    films = []

    for film_row in film_rows:
        film_data = {
            "tmdb_id": film_row[0],
            "title": film_row[1],
            "url": film_row[2],
            "screening_state": film_row[3],
            "oneliner": film_row[4],
            "img_url": film_row[5],
            "imdb_id": film_row[6],
            "lb_title": film_row[7],
            "release_year": film_row[8],
            "adult": bool(film_row[9]),  # Convert 0/1 to boolean
            "lb_url": film_row[10],
            "showings": []
        }

        # Select showings for the current film
        cursor.execute("SELECT date, time_start, time_end, location_name, location_city, show_title, ticket_url, information_url, screening_info, additional_info FROM showings WHERE tmdb_id = ?", (film_row[0],))
        showing_rows = cursor.fetchall()

        for showing_row in showing_rows:
            showing_data = {
                "date": showing_row[0],
                "time_start": showing_row[1],
                "time_end": showing_row[2],
                "location_name": showing_row[3],
                "location_city": showing_row[4],
                "show_title": showing_row[5],
                "ticket_url": showing_row[6],
                "information_url": showing_row[7],
                "screening_info": showing_row[8],
                "additional_info": showing_row[9]
            }

            film_data["showings"].append(showing_data)

        films.append(film_data)

    # Close the database connection
    db_close(conn)

    # Write the film data to a JSON file
    store_data(films, output_file)

    print("JSON file 'films_with_showings.json' has been created.") 