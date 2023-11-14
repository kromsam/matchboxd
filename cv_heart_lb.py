"""Module to run Cineville Heart Letterboxd"""
import argparse

from utils.cv_films_import import scrape_cv_film_list
from utils.cv_films_import import scrape_cv_location_list
from utils.cv_films_tmdb import add_tmdb_id
from utils.lb_films_import import get_letterboxd_data
from utils.cv_data_import import get_cv_film_data
from utils.cv_data_import import scrape_cv_film_data
from utils.generate_json import generate_json

from utils.db_utils import db_add_cv_films
from utils.db_utils import db_add_cv_films_tmdb
from utils.db_utils import db_init
from utils.db_utils import db_add_lb_films
from utils.db_utils import db_add_showings

from utils.utils import get_cv_data
from utils.utils import run_driver
from utils.utils import load_list
from utils.utils import load_string
from utils.utils import store_data

# Hard-coded constants
CV_URL = "https://cineville.nl/films"
FILM_LIST_ELEMENTS = {
    "look_for": ("section", {"class": "card--with-header-element"}),
    "wait_for": "all-films-list__list",
}

FILM_DATA_ELEMENTS = {
    "look_for": ("div", {"class": "shows-list__day-group"}),
    "wait_for": "film-draaitijden",
}

LOCATION_LIST_ELEMENTS = {
    "look_for": ("button", {"class": "selectable-button"}),
    "wait_for": "location-select-input",
}

# Variable constants
DATABASE = "database/database.sqlite"
LOCATIONS_FILE = "input/locations.txt"
TMDB_API_KEY = "input/tmdb_api_key.txt"
LETTERBOXD_JSON_URL = "https://letterboxd-list-radarr.onrender.com/"
LB_LIST_FILE = "input/letterboxd_list.txt"
MODE = "local"
LOCATIONS_WEB_FILE = "web/cities.json"
WEB_FILE = "web/films_with_showings.json"


def cv_films_import(driver, cv_url, location_list, elements, db):
    """Import films from Cineville Films page."""
    # Cineville Films Import
    print(f"Fetching films from {cv_url}...")
    data = get_cv_data(driver, cv_url, scrape_cv_film_list, location_list, elements)
    print(f"Films fetched from {cv_url}.")
    db_add_cv_films(data, db)
    print("Data added to database")


def cv_locations_import(driver, cv_url, location_list, elements, output_file):
    """Import films from Cineville Films page."""
    # Cineville Films Import
    print(f"Fetching cities from {cv_url}...")
    data = get_cv_data(driver, cv_url, scrape_cv_location_list, location_list, elements)
    print(f"Cities fetched from {cv_url}.")
    print(data)
    store_data(data, output_file)
    print("Data added to database")


def cv_films_tmdb(db, api_key):
    """Match Cineville Films to TMBD IDs"""
    print("Fetching TMDB IDs...")
    data = add_tmdb_id(db, api_key)
    print("TMDB IDs fetched.")
    db_add_cv_films_tmdb(data, db)
    print("Data added to database")


def lb_films_import(input_file, db, url):
    """Import films from Letterboxd list."""
    print(f"Fetching data from Letterboxd-list: {load_string(input_file)}")
    data = get_letterboxd_data(input_file, url)
    print("Data found.")
    db_add_lb_films(data, db)
    print("Data added to database")


def cv_data_import(driver, location_list, db, elements, mode):
    """Import films from Cineville Film Page."""
    print("Started import of film data...")
    data = get_cv_film_data(
        driver, scrape_cv_film_data, location_list, db, elements, mode
    )
    print("Import finished.")
    db_add_showings(data, db)


def arg_parser():
    """Parse arguments."""
    parser = argparse.ArgumentParser(description="Argument Parser for Your Application")

    parser.add_argument(
        "--database",
        default=DATABASE,
        help=f"Path to the database. (default: {DATABASE})",
    )

    parser.add_argument(
        "--lb_list",
        default=LB_LIST_FILE,
        help=f"Path to the LB list file. (default: {LB_LIST_FILE})",
    )

    parser.add_argument(
        "--lb_url",
        default=LETTERBOXD_JSON_URL,
        help=f"URL for Letterboxd. (default: {LETTERBOXD_JSON_URL})",
    )

    parser.add_argument(
        "--locations_file",
        default=LOCATIONS_FILE,
        help=f"Path to the locations file. (default: {LOCATIONS_FILE})",
    )

    parser.add_argument(
        "--scrape_mode",
        default=MODE,
        choices=["full", "local"],
        help=f'Mode "full" for complete scrape, "local" to only scrape from Letterboxd list. (default: {MODE})',
    )

    parser.add_argument(
        "--tmdb_api_key",
        default=TMDB_API_KEY,
        help=f"TMDB API key. (default: {TMDB_API_KEY})",
    )

    parser.add_argument(
        "--web_file",
        default=WEB_FILE,
        help=f"Path to the web file. (default: {WEB_FILE})",
    )

    return parser


if __name__ == "__main__":
    arg_parser = arg_parser()
    args = arg_parser.parse_args()
    database = args.database
    lb_list = args.lb_list
    lb_url = args.lb_url
    locations_file = args.locations_file
    scrape_mode = args.scrape_mode
    tmdb_api_key = args.tmdb_api_key
    web_file = args.web_file

    db_init(database)

    try:
        print("Starting driver...")
        with run_driver() as scrape_driver:
            print("Starting driver...")
            cv_films_import(
                scrape_driver, CV_URL, locations_file, FILM_LIST_ELEMENTS, database
            )
            locations = load_list(locations_file)
            if "all" in locations:
                cv_locations_import(
                    scrape_driver,
                    CV_URL,
                    locations_file,
                    LOCATION_LIST_ELEMENTS,
                    LOCATIONS_WEB_FILE,
                )
            cv_films_tmdb(database, tmdb_api_key)
            if scrape_mode == "local":
                lb_films_import(lb_list, database, lb_url)
            cv_data_import(
                scrape_driver, locations_file, database, FILM_DATA_ELEMENTS, scrape_mode
            )
            print("Closing driver...")

    finally:
        # Ensure that the driver is closed, even if an exception occurred
        scrape_driver.quit()
        print("Driver closed.")
        generate_json(database, web_file, scrape_mode)
