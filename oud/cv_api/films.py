"""Module to import films from the Cineville API to the database."""
from typing import Callable

from sqlalchemy import Column, String, Integer, DateTime, Boolean
from sqlalchemy.orm import declarative_base

from cv_api_utils import fetch_from_api
from cv_api_utils import get_session
from cv_api_utils import update_database
from cv_api_utils import extract_from_embedded
from cv_api_utils import save_object_to_database


CV_NL_FILMS_API = "https://api.cineville.nl/productions?sort[title]=asc&collection[common][in][0]=now-screening"
TZ = "Europe/Amsterdam"

Base = declarative_base()


class Film(Base):
    __tablename__ = "films"
    id = Column(Integer, primary_key=True, autoincrement=True)
    tmdb_id = Column(Integer)
    cv_id = Column(String)
    title = Column(String)
    slug = Column(String)
    url = Column(String)
    screening_state = Column(String)
    oneliner = Column(String)
    img_url = Column(String)
    imdb_id = Column(String)
    lb_title = Column(String)
    release_year = Column(DateTime)
    adult = Column(Boolean)
    lb_url = Column(String)
    city = Column(String)


CreateInstance = Callable[[dict], Base]


def create_film_instance(data: dict, city) -> Film:
    # Extracting data from JSON
    cv_id = data.get("id")
    title = data.get("title")
    slug = data.get("slug")
    oneliner = data.get("localizableAttributes", {}).get("shortDescription")
    img_url = None
    if data.get("assets", {}).get("cover", {}) is not None:
        img_url = data.get("assets", {}).get("cover", {}).get("url")

    # Creating URL
    url = f"https://cineville.nl/films/{slug}"

    # Creating a new Film instance
    film = Film(
        cv_id=cv_id,
        title=title,
        slug=slug,
        url=url,
        oneliner=oneliner,
        img_url=img_url,
        city=city,
    )

    return film


def import_films(api, database, city):
    api_response = fetch_from_api(api)
    session = get_session(database)()
    Base.metadata.create_all(session.bind)
    films = extract_from_embedded(api_response, "productions")
    # print(films)
    for film in films:
        db_object_instance = create_film_instance(film, city)
        save_object_to_database(session, db_object_instance)
