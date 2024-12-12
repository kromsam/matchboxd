"""Utils for main module"""

import argparse
import logging
import os
from pathlib import Path

from .config import (
    DATABASE,
    LETTERBOXD_JSON_URL,
    MODE,
    WEB_FILE,
)
from .cv_data_import import ScrapeCVFilmPage, ScrapeConfig
from .cv_films_import import (
    scrape_cv_film_list,
    scrape_cv_location_list,
)
from .cv_films_tmdb import add_tmdb_id
from .db_utils import (
    db_add_cv_films,
    db_add_cv_films_tmdb,
    db_add_lb_films,
    db_add_showings,
)
from .lb_films_import import get_letterboxd_data
from .utils import get_cv_data, store_data


# Import root logger
logger = logging.getLogger(__name__)


APP_PATH = Path(os.path.dirname(os.path.abspath(__file__))).parent


def cv_films_import(driver, cv_url, location_list, elements, db):
    """Import films from Cineville Films page."""
    logger.info("Scraping films from %s...", cv_url)
    data = get_cv_data(driver, cv_url, scrape_cv_film_list, location_list, elements)
    logger.info("Films scraped.")
    db_add_cv_films(data, db)
    logger.info("Films added to database.")


def cv_locations_import(driver, cv_url, location_list, elements, output_file):
    """Import films from Cineville Films page."""
    logger.info("Scraping cities from %s...", cv_url)
    data = get_cv_data(driver, cv_url, scrape_cv_location_list, location_list, elements)
    logger.debug("Cities scraped.")
    logger.info(data)
    store_data(data, output_file)
    logger.info("Cities added to database.")


def cv_films_tmdb(db, api_key):
    """Match Cineville Films to TMBD IDs"""
    logger.info("Looking up TMDB ids...")
    data = add_tmdb_id(db, api_key)
    logger.debug("TMDB id look up finished.")
    db_add_cv_films_tmdb(data, db)
    logger.info("TMDB ids added to database.")


def lb_films_import(lb_list, db, url):
    """Import films from Letterboxd list."""
    logger.info("Importing data from Letterboxd-list: %s", lb_list)
    data = get_letterboxd_data(lb_list, url)
    logger.debug("Letterboxd data imported.")
    db_add_lb_films(data, db)
    logger.info("Letterboxd list added to database.")


def cv_data_import(driver, location_list, db, elements, mode):
    """Import data from Cineville film pages."""
    logger.info("Started import of film data...")
    filmpage_scrape_config = ScrapeConfig(location_list, elements, mode)
    filmpage_scraper = ScrapeCVFilmPage(driver, filmpage_scrape_config)
    data = filmpage_scraper.run_scrape(db)
    logger.debug("Import finished.")
    db_add_showings(data, db)
    logger.debug("Film data added to database.")


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
        "--log_level",
        default=os.getenv("LOG_LEVEL", "INFO"),
        help='Log-level. (default: INFO)',
    )

    parser.add_argument(
        "--app_path",
        default=APP_PATH,
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
