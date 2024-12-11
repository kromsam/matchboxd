"""Module for trying out the code."""

import logging

from api.global_constants import COUNTRY, CITY, DATABASE

from api.db_helpers import DatabaseHandler
from api.cv_api_helpers import get_api_url
from api.cv_api_helpers import fetch_data_from_api
from api.cv_api_helpers import get_start_date
from api.cv_api import import_cities_to_db
from api.cv_api import import_events_to_db
from api.cv_api import import_productions_to_db
from api.cv_api import remove_films
from api.cv_api import remove_showings
from api.tmdb_api import update_tmdb_id, update_tmdb_image

# Import the root logger
logger = logging.getLogger(__name__)


def import_cities(db_handler):
    """Import cities into the database."""
    print("Creating database session...")
    session = db_handler.create_session()
    print("Database session created.")
    country = COUNTRY
    base_url, endpoint, params = get_api_url("cities", country=country)
    cv_api_data = fetch_data_from_api(base_url, endpoint, params)
    updated_cv_cities = import_cities_to_db(session, cv_api_data, country)
    logger.info("Updated Cities: %s", updated_cv_cities)
    session.close()


def import_events(db_handler):
    """Import events into the database."""
    logger.info("Import events")
    session = db_handler.create_session()
    # clear_tables(session, Showing.__table__)
    city = CITY
    logger.info(city)
    country = COUNTRY
    logger.info(country)
    start_date = get_start_date(hours_delta=1)
    logger.info(start_date)
    base_url, endpoint, params = get_api_url(
        "events", country=country, city=city, start_date=start_date
    )
    logger.info("Fetch data from API with: %s, %s, %s", base_url, endpoint, params)
    cv_api_data = fetch_data_from_api(base_url, endpoint, params)
    updated_cv_showings, updated_cv_film_titles = import_events_to_db(
        session, cv_api_data, city
    )
    remove_showings(session, cv_api_data)
    update_tmdb_id(session, film_titles=bool(updated_cv_film_titles))
    logger.info("Updated Titles: %s", updated_cv_film_titles)
    logger.info("Updated Showings: %s", updated_cv_showings)
    session.close()


def import_productions(db_handler):
    """Import productions into the database."""
    # Replace 'your_database_path' with the path to your SQLite database file
    session = db_handler.create_session()
    logger.info("Import productions...")
    city = CITY
    country = COUNTRY
    logger.info("Getting API url...")
    base_url, endpoint, params = get_api_url("productions", country=country, city=city)
    logger.info("Fetch data from url...")
    cv_api_data = fetch_data_from_api(base_url, endpoint, params)
    updated_cv_titles = import_productions_to_db(session, cv_api_data, city=city)
    # logger.info("Updated Titles: %s", updated_cv_titles)
    remove_films(session, cv_api_data, city)
    update_tmdb_id(session, film_titles=bool(updated_cv_titles))
    session.close()


def import_tmdb_id(db_handler):
    """Import tmdb id into the database."""
    session = db_handler.create_session()
    update_tmdb_id(session)
    session.close()


def import_tmdb_image(db_handler):
    """Import tmdb image into the database."""
    session = db_handler.create_session()
    update_tmdb_image(session)
    session.close()


def main(db_handler):
    """Main."""
    import_cities(db_handler)
    import_productions(db_handler)
    import_events(db_handler)
    import_tmdb_image(db_handler)


if __name__ == "__main__":
    database_handler = DatabaseHandler(DATABASE)
    database_handler.remove_database()
    database_handler.create_all()
    main(database_handler)
