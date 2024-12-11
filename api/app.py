"""FastAPI Module"""

from functools import lru_cache
import logging
from typing import Iterator

from fastapi import APIRouter, Depends, HTTPException
from fastapi_restful.session import FastAPISessionMaker
import httpx
from sqlalchemy.orm import Session

from .config import LB_API
from .global_constants import DATABASE
from .helpers import compare_with_database, handle_films_from_database
from .lb_api import (
    fetch_external_data,
)
from .schemas import APIResponse


# Import the root logger
logger = logging.getLogger(__name__)


@lru_cache()
def _get_fastapi_sessionmaker() -> FastAPISessionMaker:
    """This function could be replaced with a global variable if preferred"""
    database_uri = DATABASE
    return FastAPISessionMaker(database_uri)


def get_db() -> Iterator[Session]:
    """FastAPI dependency that provides a sqlalchemy session"""
    yield from _get_fastapi_sessionmaker().get_db()


router = APIRouter()


@router.get("/{path:path}", response_model=APIResponse)
async def api_response(
    path: str, city: str = "", db: Session = Depends(get_db)
):
    """Create API response with data from path."""
    # Construct the URL for the external API
    external_api_url = f"{LB_API}/{path}"
    logger.debug("Fetching data from: %s", external_api_url)
    # Fetch data from external API
    async with httpx.AsyncClient() as client:
        external_data = await fetch_external_data(client, external_api_url)
    logger.debug("Data fetched.")

    # Check if the external data is not None
    if external_data is None:
        logger.error("Failed to fetch data from external API.")
        raise HTTPException(
            status_code=500, detail="Failed to fetch data from external API."
        )
    logger.debug("Starting comparison...")
    # Compare with the database
    film_ids_in_database, films_in_database = await compare_with_database(
        external_data, db
    )

    # Combine the external data, city parameter, and film_ids from the database
    combined_data = {
        "path": path,
        "city": city,
        "films_with_showings": [],
    }

    combined_data["films_with_showings"] = handle_films_from_database(
        films_in_database, external_data
    )

    return combined_data
