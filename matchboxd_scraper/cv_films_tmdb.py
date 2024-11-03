"""Add TMDB ids to a list of films"""

import logging
import re

import requests

from matchboxd_scraper.db_utils import load_db_data


# Import root logger
logger = logging.getLogger(__name__)


def add_tmdb_id(db, api_key):
    """Add tmdb id to json file"""
    query = "SELECT * FROM films"
    films = load_db_data(db, query)
    for film in films:
        movie_title = film["title"]
        logger.info(movie_title)
        movie_id = get_movie_id(movie_title, api_key)
        if movie_id is None:
            if "(" in movie_title or ")" in movie_title:
                # Define a regular expression pattern to remove text inside parentheses
                pattern = r"\([^)]*\)"

                # Use the re.sub() function to remove text inside parentheses
                cleaned_title = re.sub(pattern, "", movie_title)

                # Remove any trailing hyphens and extra spaces
                cleaned_title = cleaned_title.strip()
                cleaned_title = re.sub(r"-+$", "", cleaned_title)
                movie_id = get_movie_id(cleaned_title, api_key)
                logger.info("Tried: %s", cleaned_title)
            if ":" in movie_title:
                logger.debug("Trying again removing everything after : .")
                cleaned_title = re.sub(r":.*", "", movie_title)
                cleaned_title.strip()
                movie_id = get_movie_id(cleaned_title, api_key)
                logger.info("Tried: %s", cleaned_title)
                if movie_id is None:
                    logger.debug("Trying again removing everything before : .")
                    pattern = r":\s(.*)$"
                    cleaned_title = re.sub(
                        pattern, ":", movie_title, flags=re.MULTILINE
                    )
                    movie_id = get_movie_id(cleaned_title, api_key)
                    logger.info("Tried: %s", cleaned_title)
        if movie_id is None:
            logger.info("TMDB id not found.")
        film["tmdb_id"] = movie_id
        if movie_id:
            logger.info("TMDB id: %s", movie_id)
    return films


def get_movie_id(movie_title, api_key):
    """Get tmdb id from movie title"""
    base_url = "https://api.themoviedb.org/3/search/movie"
    params = {"api_key": api_key, "query": movie_title}
    response = requests.get(base_url, params=params, timeout=20)
    tmdb_data = response.json()
    if tmdb_data.get("results"):
        return tmdb_data["results"][0]["id"]
    return None
