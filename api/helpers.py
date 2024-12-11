"""Helpers for app."""

from datetime import datetime
from itertools import zip_longest
from urllib.parse import urlparse, parse_qs
import logging

from fastapi import HTTPException
from sqlalchemy.orm import Session

from .models import Film
from .schemas import FilmSchema

# Import the root logger
logger = logging.getLogger(__name__)


async def compare_with_database(response_data, db: Session):
    """Compare database with external, match tmdb ids."""
    # Assuming response_data is a list of dictionaries
    external_tmdb_ids = [
        entry["id"]
        for entry in response_data
        if isinstance(entry, dict) and "id" in entry
    ]
    try:
        # Query the database to get films for matching tmdb_ids
        logger.debug("Querying database for matching films.")
        films_in_database = (
            db.query(Film).filter(Film.tmdb_id.in_(external_tmdb_ids)).all()
        )
        logger.debug("Matching films: %s", films_in_database)
        # Extract film_ids from the database result
        film_ids_in_database = [film.id for film in films_in_database]

        return film_ids_in_database, films_in_database
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e)) from e


def get_films_in_database_dict(films_in_database):
    """Create a dictionary of all films in database"""
    if films_in_database is not None:
        # Convert records to dictionaries
        film_schema = FilmSchema()
        films_in_database_dict = [film_schema.dump(film) for film in films_in_database]
        return films_in_database_dict


def handle_films_from_database(films_in_database, external_data):
    """Handle Letterboxd film data."""
    if external_data is not None:
        films_from_database = []

        # Use zip_longest to iterate over both lists, filling missing values with None

        films_in_database_dict = get_films_in_database_dict(films_in_database)

        if films_in_database_dict is None:
            raise ValueError("films_in_database_dict is None")

        # Create a dictionary for faster lookup based on tmdb_id
        films_in_database_dict_dict = {
            film["tmdb_id"]: film 
            for film in films_in_database_dict 
            if isinstance(film, dict) and film is not None
        }

        # Iterate through external_data
        for entry in external_data:
            external_id = entry.get("id")

            # Check if external_id is present in films_in_database_dict
            if external_id in films_in_database_dict_dict:
                entry.pop("id", None)
                # Merge the dictionaries
                films_in_database_dict_dict[external_id].update(entry)

        # The merged data is now in films_in_database_dict
        # If you need it as a list, you can extract values from the dictionary
        merged_data_list = list(films_in_database_dict_dict.values())

    else:
        logger.error("Error: Films in the database or external data is None.")
    return merged_data_list


def handle_showings(film):
    """Add showings to films."""
    showings_data = []
    for showing in film.get("showings"):
        start_date = datetime.fromisoformat(showing.get("start_date", ""))
        end_date = datetime.fromisoformat(showing.get("end_date", ""))
        showings_data.append(
            {
                "date": start_date.strftime("%Y-%m-%d"),
                "time_start": start_date.strftime("%H:%M"),
                "time_end": end_date.strftime("%H:%M"),
                "location_name": showing.get("location_name", ""),
                "location_city": showing.get("location_city", ""),
                "show_title": film.get("title", None),
                "ticket_url": showing.get("ticket_url", ""),
                "information_url": showing.get("information_url", ""),
                "screening_info": showing.get("screening_info", ""),
                "additional_info": showing.get("additional_info", ""),
            }
        )
    return showings_data


def extract_api_url(url):
    """Extract base_url, endpoint and params from url"""
    # Parse the URL
    parsed_url = urlparse(url)

    # Extract base URL
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

    # Extract endpoint
    endpoint = parsed_url.path

    # Extract query parameters and convert them to a dictionary
    params = parse_qs(parsed_url.query)

    # Convert list values to single values where applicable
    params = {k: v[0] if len(v) == 1 else v for k, v in params.items()}

    return base_url, endpoint, params
