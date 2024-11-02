"""Module to run Cineville Heart Letterboxd"""

import argparse
import os

from config import (
    CV_URL,
    FILM_LIST_ELEMENTS,
    FILM_DATA_ELEMENTS,
    LOCATION_LIST_ELEMENTS,
    APP_PATH,
    DATABASE,
    LETTERBOXD_JSON_URL,
    MODE,
    LOCATIONS_WEB_FILE,
    LB_LIST_FILE,
    WEB_FILE,
)
from utils.cv_data_import import ScrapeCVFilmPage, ScrapeConfig
from utils.cv_films_import import scrape_cv_film_list, scrape_cv_location_list
from utils.cv_films_tmdb import add_tmdb_id
from utils.db_utils import (
    db_add_cv_films,
    db_add_cv_films_tmdb,
    db_add_lb_films,
    db_add_showings,
    db_init,
)
from utils.generate_json import generate_json
from utils.lb_films_import import get_letterboxd_data
from utils.utils import get_cv_data, load_list, run_driver, store_data


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
    filmpage_scrape_config = ScrapeConfig(location_list, elements, mode)
    filmpage_scraper = ScrapeCVFilmPage(driver, filmpage_scrape_config)
    data = filmpage_scraper.run_scrape(db)
    print("Import finished.")
    db_add_showings(data, db)


def create_arg_parser():
    """Parse arguments."""
    parser = argparse.ArgumentParser(description="Argument Parser for Your Application")

    parser.add_argument(
        "--database",
        default=os.getenv("DATABASE", DATABASE),
        help=f"Path to the database. (default: {DATABASE})",
    )

    parser.add_argument(
        "--lb_list",
        default=os.getenv(
            "LB_LIST", "bfi/list/sight-and-sounds-greatest-films-of-all-time/"
        ),
        help="""
            Path to the LB list file.
            (default: Sight and Sounds Greatest Films of All Time 2022)
        """,
    )

    parser.add_argument(
        "--lb_url",
        default=os.getenv("LB_URL", LETTERBOXD_JSON_URL),
        help=f"URL for Letterboxd. (default: {LETTERBOXD_JSON_URL})",
    )

    parser.add_argument(
        "--locations",
        default=os.getenv("LOCATIONS", "all"),
        help='Comma-separated list of cities, or: "all". (default: all)',
    )

    parser.add_argument(
        "--app_path",
        default=os.getenv("APP_PATH", APP_PATH),
        help=f"Path to app. (default: {APP_PATH})",
    )

    parser.add_argument(
        "--scrape_mode",
        default=os.getenv("SCRAPE_MODE", MODE),
        choices=["full", "local"],
        help=f"""
            Mode "full" for complete scrape,
            "local" to only scrape from Letterboxd list. (default: {MODE})
        """,
    )

    parser.add_argument(
        "--tmdb_api",
        default=os.getenv("TMDB_API"),
        help="TMDB API key.)",
    )

    parser.add_argument(
        "--web_file",
        default=os.getenv("WEB_FILE", WEB_FILE),
        help=f"Path to the web file. (default: {WEB_FILE})",
    )

    return parser


if __name__ == "__main__":
    print("Starting matchboxd...")

    arg_parser = create_arg_parser()
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
