"""City, Film and Showing models."""

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
)
from sqlalchemy.orm import relationship

from .db_helpers import Base

# Define the association table for the many-to-many relationship
film_city_association = Table(
    "film_city_association",
    Base.metadata,
    Column("film_id", Integer, ForeignKey("films.id")),
    Column("city_id", Integer, ForeignKey("cities.id")),
)


class City(Base):
    """SQLAlchemy class for City."""

    __tablename__ = "cities"
    id = Column(Integer, primary_key=True, autoincrement=True)
    city_slug = Column(String)
    city_name = Column(String)
    country = Column(String)
    timestamp = Column(DateTime)

    # Add the relationship to films
    films = relationship(
        "Film", secondary=film_city_association, back_populates="cities"
    )


class Film(Base):
    """SQLAlchemy class for Film."""

    __tablename__ = "films"
    id = Column(Integer, primary_key=True, autoincrement=True)
    tmdb_id = Column(Integer)
    cv_film_id = Column(String, unique=True)
    title = Column(String)
    slug = Column(String)
    screening_state = Column(String)
    oneliner = Column(String)
    img_url = Column(String)

    # Establish the many-to-many relationship with City
    cities = relationship(
        "City", secondary=film_city_association, back_populates="films"
    )

    # Define the relationship to the Showings table
    showings = relationship("Showing", back_populates="film")


class Showing(Base):
    """SQLAlchemy class for Showing."""

    __tablename__ = "showings"
    id = Column(Integer, primary_key=True, autoincrement=True)
    cv_showing_id = Column(String, unique=True)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    location_name = Column(String)
    location_city = Column(String)
    ticket_url = Column(String)
    information_url = Column(String)
    screening_info = Column(String)
    additional_info = Column(String)

    # Define the relationship to the Films table
    film_id = Column(Integer, ForeignKey("films.id"))
    film = relationship("Film", back_populates="showings")
