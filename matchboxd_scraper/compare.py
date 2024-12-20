"""Compare two lists for matching tmdb ids, and put the result in a new list."""

import logging

from .utils import load_json_data


# Import root logger
logger = logging.getLogger(__name__)


def compare_for_tmdb(cv_films, lb_films):
    """Compare two lists for matching tmdb ids"""
    cv_films_data = load_json_data(cv_films)
    logger.info("Loaded data from: %s", cv_films)
    lb_films_data = load_json_data(lb_films)
    logger.info("Loaded data from: %s", lb_films)

    # Create a dictionary to store films with matching tmdb_id
    common_films = {}

    # Iterate through cv_films to find common films
    for cv_film in cv_films_data:
        tmdb_id = cv_film.get("tmdb_id")
        lb_film = next(
            (film for film in lb_films_data if film.get("tmdb_id") == tmdb_id), None
        )

        if lb_film:
            # Create a new dictionary with the merged data
            merged_film = {
                "title": cv_film.get("title"),
                "tmdb_id": tmdb_id,
                "url": cv_film.get("url"),
                "screening_state": cv_film.get("screening_state"),
                "oneliner": cv_film.get("oneliner"),
                "img_url": cv_film.get("img_url"),
                "imdb_id": lb_film.get("imdb_id"),
                "lb_title": lb_film.get("title"),
                "release_year": lb_film.get("release_year"),
                "adult": lb_film.get("adult"),
                "lb_url": lb_film.get("url"),
            }

            common_films[tmdb_id] = merged_film

    common_films_list = list(common_films.values())
    logger.info("Comparison succeeded.")
    logger.debug("Films in common: %s", common_films_list)
    return common_films_list
