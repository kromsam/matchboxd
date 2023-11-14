# https://chat.openai.com/c/cec4fdaa-2b9a-4b1d-ba29-af06e8833e7d
#
from sqlalchemy import create_engine, Column, Integer, String, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import requests

Base = declarative_base()


class Film(Base):
    __tablename__ = "films"
    id = Column(Integer, primary_key=True, autoincrement=True)
    tmdb_id = Column(Integer)
    cv_id = Column(String, unique=True)
    title = Column(String)
    slug = Column(String)
    url = Column(String)
    screening_state = Column(String)
    oneliner = Column(String)
    img_url = Column(String)
    cities = Column(JSON)


# Replace 'your_database_path' with the path to your SQLite database file
engine = create_engine("sqlite:///your_database_path.db", echo=True)
Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine)
session = Session()


def fetch_data_from_api(city):
    api_url = f"https://api.example.com/films?city={city}"
    response = requests.get(api_url)
    return response.json()


def update_database(api_data, city):
    updated_titles = []

    for data in api_data["_embedded"]["productions"]:
        cv_id = data.get("id")
        title = data.get("title")
        slug = data.get("slug")
        oneliner = data.get("localizableAttributes", {}).get("shortDescription")
        img_url = None
        if data.get("assets", {}).get("cover", {}) is not None:
            img_url = data.get("assets", {}).get("cover", {}).get("url")
        url = f"https://cineville.nl/films/{slug}"

        film = session.query(Film).filter_by(cv_id=cv_id).first()

        if film is None:
            # Film not in the database, add it
            new_film = Film(
                cv_id=cv_id,
                title=title,
                slug=slug,
                url=url,
                oneliner=oneliner,
                img_url=img_url,
                cities=[city],
            )
            session.add(new_film)
            updated_titles.append(title)
        else:
            # Film already in the database, update if necessary
            if film.title != title:
                updated_titles.append(title)
                film.title = title
            # Check if the queried city is in the 'cities' list
            if city not in film.cities:
                film.cities.append(city)

    # Remove films that are not in the API response
    for film in session.query(Film).all():
        if (
            film.cities
            and city in film.cities
            and film.cv_id
            not in [data.get("id") for data in api_data["_embedded"]["productions"]]
        ):
            film.cities.remove(city)
            if len(film.cities) == 0:
                session.delete(film)

    session.commit()
    return updated_titles


# Replace 'your_city' with the desired city for the API query
api_data = fetch_data_from_api("your_city")
updated_titles = update_database(api_data, "your_city")

print("Updated Titles:", updated_titles)
