from cities import import_cities
from cities import CV_NL_CITIES_API
from films import import_films
from films import CV_NL_FILMS_API

DATABASE = "database/database.sqlite"
COUNTRY = "nl"

import_cities(CV_NL_CITIES_API, f"sqlite:///{DATABASE}")
import_films(CV_NL_FILMS_API, f"sqlite:///{DATABASE}")
