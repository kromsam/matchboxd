"""Global constants."""

from config import (
    DB_HOST,
    DB_NAME,
    DB_PASSWORD,
    DB_PORT,
    DB_TYPE,
    DB_USER,
)

# Database
DATABASE = f"{DB_TYPE}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Types
TYPE_CITIES = "cities"
TYPE_EVENTS = "events"
TYPE_PRODUCTIONS = "productions"
