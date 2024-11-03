"""Configuration."""

# Settings
COUNTRY = "nl"
CITY = None

# Database
DB_TYPE = "postgresql"
DB_NAME = "matchboxd_db"
DB_USER = "matchboxd_db"
DB_PASSWORD = "123_123"
DB_HOST = "matchboxd_db"
DB_PORT = "5432"

# Cineville API
CV_API = {"nl": "https://api.cineville.nl",
          "be": "https://api.cinevillepass.be"}

# Letterboxd API
LB_API = "https://letterboxd-list-radarr.onrender.com"

# The Movie Database API
TMDB_API = "https://api.themoviedb.org/3"
TMDB_API_KEY = ""

# Logging
LOG_LEVEL = "DEBUG"
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
