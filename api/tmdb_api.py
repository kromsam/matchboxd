"""Modules to handle request to TMDB API."""

import logging
import re

import httpx

from .config import TMDB_API
from .config import TMDB_API_KEY
from .models import Film

# Import the root logger
logger = logging.getLogger(__name__)


def get_tmdb_id(film_title):
    """Get tmdb id from movie title"""
    base_url = TMDB_API + "/search/movie"
    api_key = TMDB_API_KEY
    params = {"api_key": api_key, "query": film_title}
    response = httpx.get(base_url, params=params, timeout=20)
    tmdb_data = response.json()
    if tmdb_data.get("results"):
        return tmdb_data["results"][0]["id"]
    return None


def get_tmdb_img(tmdb_id):
    """Get tmdb image from movie title"""
    base_url = TMDB_API + "/movie/" + str(tmdb_id) + "/images"
    api_key = TMDB_API_KEY
    params = {"api_key": api_key}
    response = httpx.get(base_url, params=params, timeout=20)
    print(response.url)
    tmdb_data = response.json()
    if tmdb_data.get("backdrops"):
        return tmdb_data.get("backdrops")[0]["file_path"]
    return None


def update_tmdb_id(session, film_titles=False):
    """Update the TMDB ID for given films."""
    if film_titles is False:
        # Otherwise, load all films from the database
        films = session.query(Film).all()
    elif film_titles:
        # If film_titles is provided, filter films based on the given titles
        films = session.query(Film).filter(Film.title.in_(film_titles)).all()
    else:
        logger.info("No films to update.")
        return
    logger.info("Films loaded.")

    for film in films:
        film_title = film.title
        logger.info("Searching TMDB id for: %s", film_title)
        film_id = get_tmdb_id(film_title)
        if film_id is None:
            if "(" in film_title or ")" in film_title:
                logger.info("Film not found, trying again without ().")
                # Define a regular expression pattern to remove text inside parentheses
                pattern = r"\([^)]*\)"

                # Use the re.sub() function to remove text inside parentheses
                cleaned_title = re.sub(pattern, "", film_title)

                # Remove any trailing hyphens and extra spaces
                cleaned_title = cleaned_title.strip()
                cleaned_title = re.sub(r"-+$", "", cleaned_title)
                film_id = get_tmdb_id(cleaned_title)
            if ":" in film_title:
                logger.info(
                    "Film not found, trying again removing everything after : ."
                )
                cleaned_title = re.sub(r":.*", "", film_title)
                cleaned_title.strip()
                film_id = get_tmdb_id(cleaned_title)
                if film_id is None:
                    logger.info(
                        "Film not found, trying again removing everything before : ."
                    )
                    pattern = r":\s(.*)$"
                    cleaned_title = re.sub(pattern, ":", film_title, flags=re.MULTILINE)
                    film_id = get_tmdb_id(cleaned_title)
        if film_id is None:
            logger.info("Film not found.")
        film.tmdb_id = film_id
        session.commit()
        log_string = f"{film_title}: {film_id}"
        logger.info("TMDB id for %s.", log_string)


def update_tmdb_image(session):
    films = session.query(Film).filter(Film.img_url.is_(None)).all()
    for film in films:
        img_path = get_tmdb_img(film.tmdb_id)
        if img_path:
            film.img_url = "https://image.tmdb.org/t/p/original" + img_path
        else:
            film.img_url = None
        session.commit()
        logger.info("Image for %s updated.", film.title)