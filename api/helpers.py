"""Helpers for app."""

from datetime import datetime
from itertools import zip_longest
import logging

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models import Film
from schemas import FilmSchema

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
        films_in_database = (
            db.query(Film).filter(Film.tmdb_id.in_(external_tmdb_ids)).all()
        )

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

        # Create a dictionary for faster lookup based on tmdb_id
        films_in_database_dict_dict = {
            film["tmdb_id"]: film for film in films_in_database_dict
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
