"""Pydantic schemas."""
from typing import List, Optional

from marshmallow_sqlalchemy import fields, SQLAlchemyAutoSchema
from pydantic import BaseModel

from .models import City, Film, Showing


class APIResponse(BaseModel):
    """Pydantic model for API response."""

    path: str
    city: Optional[str] = None
    films_with_showings: List[dict]


class CitySchema(SQLAlchemyAutoSchema):
    """Pydantic model for City."""

    class Meta:
        """City schema options."""

        model = City
        include_fk = True


class ShowingSchema(SQLAlchemyAutoSchema):
    """Pydantic model for Showing."""

    class Meta:
        """Showing schema options."""

        model = Showing
        include_fk = True


class FilmSchema(SQLAlchemyAutoSchema):
    """Pydantic model for Film."""

    cities = fields.Nested(CitySchema, many=True)
    showings = fields.Nested(ShowingSchema, many=True)

    class Meta:
        """Film schema options."""

        model = Film
        include_fk = True
        include_relationships = True
