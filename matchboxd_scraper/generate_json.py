"""Generate json-file from database."""

from matchboxd_scraper.db_utils import db_commit_close, db_conn
from matchboxd_scraper.utils import store_data


def generate_json(db, output_file, scrape_mode):
    """Generate a json-file from the film database."""
    conn = db_conn(db, "ro")
    cursor = conn.cursor()
    query = ""

    # Define the query to select films with lb_check is true
    if scrape_mode == "local":
        query = """
        SELECT tmdb_id, title, url, screening_state, oneliner,
        img_url, imdb_id, lb_title, release_year, adult, lb_url
        FROM films
        WHERE lb_check = 1
        """
    elif scrape_mode == "full":
        query = """
        SELECT tmdb_id, title, url, screening_state,
        oneliner, img_url, imdb_id, lb_title, release_year, adult, lb_url
        FROM films
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
            "showings": [],
        }
        if film_row[9] is None:
            film_data["adult"] = None

        # Select showings for the current film
        cursor.execute(
            """
            SELECT date, time_start, time_end, location_name, location_city,
            show_title, ticket_url, information_url, screening_info, additional_info
            FROM showings WHERE tmdb_id = ?
            """,
            (film_row[0],),
        )
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
                "additional_info": showing_row[9],
            }

            film_data["showings"].append(showing_data)

        films.append(film_data)

    # Close the database connection
    db_commit_close(conn)

    # Write the film data to a JSON file
    store_data(films, output_file)

    print(f"JSON file {output_file} has been created.")
