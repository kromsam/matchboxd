"""Module to import cities from the Cineville API to the database."""
from datetime import datetime
from typing import Callable

from functools import partial

import pytz
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.orm import declarative_base

from cv_api_utils import fetch_from_api
from cv_api_utils import get_session
from cv_api_utils import update_database
from cv_api_utils import extract_from_embedded

CV_NL_CITIES_API = (
    "https://api.cineville.nl/collections?collectionGroupId[in][0]=cities"
)
TZ = "Europe/Amsterdam"

Base = declarative_base()


class City(Base):
    __tablename__ = "cities"
    id = Column(Integer, primary_key=True, autoincrement=True)
    slug = Column(String)
    full_name = Column(String)
    country = Column(String)
    timestamp = Column(DateTime)


CreateInstance = Callable[[dict], Base]


def create_city_instance(data: dict, timezone: str, country: str) -> City:
    # Add the city to the 'cities' table
    timezone = pytz.timezone(timezone)
    current_time = datetime.now(timezone)

    city = City(
        slug=data["id"],
        full_name=format_city_name(data["id"]),
        country=country,
        timestamp=current_time,
    )
    return city


def format_city_name(name):
    # Custom function to format city names
    parts = name.split("-")
    formatted_name = " ".join(
        part.capitalize() if not part.startswith("ij") else "IJ" + part[2:].capitalize()
        for part in parts
    )
    print(parts)
    return formatted_name


def import_cities(api, database):
    api_response = fetch_from_api(api)
    session = get_session(database)()
    Base.metadata.create_all(session.bind)
    update_database(
        api_response=api_response,
        extract_function=partial(extract_from_embedded, json_value="collections"),
        api_entity_attr="id",
        session=session,
        db_entity_attr="slug",
        instance_function=create_city_instance,
        db_object_class=City,
        timezone=TZ,
        country="nl",
    )
