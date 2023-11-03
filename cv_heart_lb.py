"""Module to run Cineville Heart Letterboxd"""
import argparse

from cv_films_import import scrape_cv_film_list
from cv_films_tmdb import add_tmdb_id
from lb_films_import import get_letterboxd_data
from cv_data_import import get_cv_film_data
from cv_data_import import scrape_cv_film_data
from generate_json import generate_json

from db_utils import db_add_cv_films
from db_utils import db_add_cv_films_tmdb
from db_utils import db_init
from db_utils import db_add_lb_films
from db_utils import db_add_showings

from utils import get_cv_data
from utils import run_driver
from utils import get_lb_list

# Hard-coded constants
CV_URL = "https://cineville.nl/films"
FILM_LIST_LOOK_FOR = ('li', {'data-colspan': '1'})
FILM_LIST_WAIT_FOR = "all-films-list__list"
FILM_DATA_LOOK_FOR = ('div', {'class': 'shows-list__day-group'})
FILM_DATA_WAIT_FOR = "film-draaitijden"

# Variable constants
DATABASE = "output/database.sqlite"
LOCATIONS_FILE = "input/locations.txt"
TMDB_API_KEY = "input/tmdb_api_key.txt"
LETTERBOXD_JSON_URL = "https://letterboxd-list-radarr.onrender.com/"
LB_LIST_FILE = "input/letterboxd_list.txt"
WEB_FILE = "web/films_with_showings.json"


def cv_films_import(driver, cv_url, locations, wait_for, look_for, db):
    """Import films from Cineville Films page."""
    # Cineville Films Import
    print(f"Fetching data from {cv_url}...")
    data = get_cv_data(driver, cv_url, scrape_cv_film_list, locations, wait_for, look_for)
    print(f"Data fetched from {cv_url}.")
    db_add_cv_films(data, db)
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
    print(f"Fetching data from Letterboxd-list: {get_lb_list(input_file)}")
    data = get_letterboxd_data(input_file, url)
    print("Data found.")
    db_add_lb_films(data, db)
    print("Data added to database")


def cv_data_import(driver, locations, db, wait_for, look_for):
    """Import films from Cineville Film Page."""
    print("Started import of film data...")
    data = get_cv_film_data(driver, scrape_cv_film_data, locations, db, wait_for, look_for)
    print("Import finished.")
    db_add_showings(data, db)


def arg_parser():
    """Parse arguments."""
    parser = argparse.ArgumentParser(description="Argument Parser for Your Application")

    parser.add_argument(
        '--database',
        default=DATABASE,
        help=f'Path to the database. (default: {DATABASE})'
    )

    parser.add_argument(
        '--lb_list',
        default=LB_LIST_FILE,
        help=f'Path to the LB list file. (default: {LB_LIST_FILE})'
    )

    parser.add_argument(
        '--lb_url',
        default=LETTERBOXD_JSON_URL,
        help=f'URL for Letterboxd. (default: {LETTERBOXD_JSON_URL})'
    )

    parser.add_argument(
        '--locations_file',
        default=LOCATIONS_FILE,
        help=f'Path to the locations file. (default: {LOCATIONS_FILE})'
    )

    parser.add_argument(
        '--tmdb_api_key',
        default=TMDB_API_KEY,
        help=f'TMDB API key. (default: {TMDB_API_KEY})'
    )

    parser.add_argument(
        '--web_file',
        default=WEB_FILE,
        help=f'Path to the web file. (default: {WEB_FILE})'
    )

    return parser


if __name__ == "__main__":
    arg_parser = arg_parser()
    args = arg_parser.parse_args()
    database = args.database
    lb_list = args.lb_list
    lb_url = args.lb_url
    locations_file = args.locations_file
    tmdb_api_key = args.tmdb_api_key
    web_file = args.web_file

    db_init(database)

    print("Starting driver...")
    scrape_driver = run_driver()

    cv_films_import(scrape_driver, CV_URL, locations_file, FILM_LIST_WAIT_FOR, FILM_LIST_LOOK_FOR, database)
    cv_films_tmdb(database, tmdb_api_key)
    lb_films_import(lb_list, database, lb_url)
    cv_data_import(scrape_driver, locations_file, database, FILM_DATA_WAIT_FOR, FILM_DATA_LOOK_FOR)
    print("Closing driver...")
    scrape_driver.quit()
    print("Driver closed.")
    generate_json(database, web_file)
