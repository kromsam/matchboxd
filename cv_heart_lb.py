"""Module to run Cineville Heart Letterboxd"""
import os
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
APP_PATH = "/usr/src/app"
DATABASE = "database/database.sqlite"
LETTERBOXD_JSON_URL = "https://letterboxd-list-radarr.onrender.com/"
MODE = "local"
LOCATIONS_WEB_FILE = "web/data/cities.json"
LB_LIST_FILE = "web/data/lb_list.json"
WEB_FILE = "web/data/films_with_showings.json"

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


def lb_films_import(lb_list, db, url):
    """Import films from Letterboxd list."""
    print(f"Fetching data from Letterboxd-list: {lb_list}")
    data = get_letterboxd_data(lb_list, url)
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
        default=os.getenv('DATABASE', DATABASE),
        help=f"Path to the database. (default: {DATABASE})",
    )

    parser.add_argument(
        "--lb_list",
        default=os.getenv(
            "LB_LIST", "bfi/list/sight-and-sounds-greatest-films-of-all-time/"
        ),
        help="Path to the LB list file. (default: Sight and Sounds Greatest Films of All Time 2022)",
    )

    parser.add_argument(
        "--lb_url",
        default=os.getenv('LB_URL', LETTERBOXD_JSON_URL),
        help=f"URL for Letterboxd. (default: {LETTERBOXD_JSON_URL})",
    )

    parser.add_argument(
        "--locations",
        default=os.getenv("LOCATIONS", "all"),
        help='Comma-separated list of cities, or: "all". (default: all)',
    )

    parser.add_argument(
        "--app_path",
        default=os.getenv('APP_PATH', APP_PATH),
        help=f"Path to app. (default: {APP_PATH})",
    )

    parser.add_argument(
        "--scrape_mode",
        default=os.getenv("SCRAPE_MODE", MODE),
        choices=["full", "local"],
        help=f'Mode "full" for complete scrape, "local" to only scrape from Letterboxd list. (default: {MODE})',
    )

    parser.add_argument(
        "--tmdb_api",
        default=os.getenv("TMDB_API"),
        help="TMDB API key.)",
    )

    parser.add_argument(
        "--web_file",
        default=os.getenv('WEB_FILE', WEB_FILE),
        help=f"Path to the web file. (default: {WEB_FILE})",
    )

    return parser


if __name__ == "__main__":
    print("Starting matchboxd...")

    arg_parser = arg_parser()
    args = arg_parser.parse_args()
    database = args.database
    lb_list_string = args.lb_list
    lb_url = args.lb_url
    locations_string = args.locations
    scrape_mode = args.scrape_mode
    tmdb_api = args.tmdb_api
    locations_web_file = args.app_path + "/" + LOCATIONS_WEB_FILE
    lb_list_file = args.app_path + "/" + LB_LIST_FILE
    web_file = args.app_path + "/" + args.web_file

    if tmdb_api is None:
        print("You need to provide a TMDB API key with --tmdb_api.")
    if locations_string is None:
        print("You need to provide locations with --locations.")

    db_init(database)

    try:
        print("Starting driver...")
        with run_driver() as scrape_driver:
            locations = load_list(locations_string)
            print("Starting driver...")
            cv_films_import(
                scrape_driver, CV_URL, locations, FILM_LIST_ELEMENTS, database
            )
            if "all" in locations:
                cv_locations_import(
                    scrape_driver,
                    CV_URL,
                    locations,
                    LOCATION_LIST_ELEMENTS,
                    locations_web_file,
                )
            else:
                store_data(locations, locations_web_file)

            cv_films_tmdb(database, tmdb_api)
            if scrape_mode == "local":
                lb_films_import(lb_list_string, database, lb_url)
            cv_data_import(
                scrape_driver, locations, database, FILM_DATA_ELEMENTS, scrape_mode
            )
            print("Closing driver...")

    finally:
        # Ensure that the driver is closed, even if an exception occurred
        scrape_driver.quit()
        print("Driver closed.")
        store_data(lb_list_string, lb_list_file)
        generate_json(database, web_file, scrape_mode)
