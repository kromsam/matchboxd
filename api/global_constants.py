"""Global constants."""

import tomllib
import os

config_path = os.getenv("API_CONFIG_PATH", "config.toml")

with open(config_path, "rb") as f:
    config = tomllib.load(f)

# Settings
COUNTRY = os.getenv("COUNTRY", config["location"]["country"])
CITY = os.getenv("CITY", config["location"]["city"])

# Database
DB_TYPE = os.getenv("DB_TYPE", config["database"]["type"])
DB_NAME = os.getenv("DB_NAME", config["database"]["name"])
DB_USER = os.getenv("DB_USER", config["database"]["user"])
DB_PASSWORD = os.getenv("DB_PASSWORD", config["database"]["password"])
DB_HOST = os.getenv("DB_HOST", config["database"]["host"])
DB_PORT = os.getenv("DB_PORT", config["database"]["port"])

# Cineville API
CV_API = {
    key: os.getenv(f"CV_API_{key.upper()}", value)
    for key, value in config["cv_api"].items()
}

# Letterboxd List API
LB_LIST_API = os.getenv("LB_LIST_API", config["lb_list_api"]["url"])

# The Movie Database API
TMDB_API = os.getenv("TMDB_API", config["tmdb_api"]["url"])
TMDB_API_KEY = os.getenv("TMDB_API_KEY", config["tmdb_api"]["key"])

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", config["logging"]["level"])
LOG_FORMAT = os.getenv("LOG_FORMAT", config["logging"]["format"])

# Do not edit

# Database
DATABASE = f"{DB_TYPE}+psycopg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Types
TYPE_CITIES = "cities"
TYPE_EVENTS = "events"
TYPE_PRODUCTIONS = "productions"
