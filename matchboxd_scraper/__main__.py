"""Module to run Cineville Heart Letterboxd"""

import logging

from main_utils import (
    create_arg_parser,
    cv_films_import,
    cv_locations_import,
    cv_films_tmdb,
    lb_films_import,
    cv_data_import,
)
from config import (
    LOCATIONS_WEB_FILE,
    LB_LIST_FILE,
    LOG_FORMAT,
)
from global_constants import (
    CV_URL,
    FILM_LIST_ELEMENTS,
    FILM_DATA_ELEMENTS,
    LOCATION_LIST_ELEMENTS,
)
from db_utils import db_init
from utils import run_driver, store_data, load_list
from generate_json import generate_json


# Parse arguments

arg_parser = create_arg_parser()
args = arg_parser.parse_args()
log_level = args.log_level
database = args.database
lb_list_string = args.lb_list
lb_url = args.lb_url
locations_string = args.locations
scrape_mode = args.scrape_mode
tmdb_api = args.tmdb_api
locations_web_file = args.app_path / LOCATIONS_WEB_FILE
lb_list_file = args.app_path / LB_LIST_FILE
web_file = args.app_path / args.web_file

# Set up logging

# Map the string representation to the corresponding logging level constant
NUMERIC_LOG_LEVEL = getattr(logging, log_level, None)

logging.basicConfig(
    level=NUMERIC_LOG_LEVEL,
    format=LOG_FORMAT,
    handlers=[
        logging.StreamHandler(),
        # Add other handlers if needed
    ],
)

# Import root logger
logger = logging.getLogger(__name__)

logger.info("Starting matchboxd...")


if tmdb_api is None:
    logger.error("You need to provide a TMDB API key with --tmdb_api.")
if locations_string is None:
    logger.error("You need to provide locations with --locations.")

logger.info("Letterboxd list: %s", lb_list_string)
logger.info("Locations: %s", locations_string)

locations = load_list(locations_string)

db_init(database)

try:
    logger.debug("Starting driver...")
    with run_driver() as scrape_driver:
        logger.info("Driver started.")

        cv_films_import(scrape_driver, CV_URL, locations, FILM_LIST_ELEMENTS, database)
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

finally:
    # Ensure that the driver is closed, even if an exception occurred
    logger.info("Closing driver...")
    scrape_driver.quit()
    logger.info("Driver closed.")
    store_data(lb_list_string, lb_list_file)
    generate_json(database, web_file, scrape_mode)
