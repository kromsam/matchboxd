# Hard-coded constants
CV_URL = "https://cineville.nl/films"
FILM_LIST_ELEMENTS = {
    "look_for": ("section", {"class": "card--with-header-element"}),
    "wait_for": "all-films-list__list",
}

FILM_DATA_ELEMENTS = {
    "look_for": ("div", {"class": "shows-list__day-group"}),
    "wait_for": "film-draaitijden",
}

LOCATION_LIST_ELEMENTS = {
    "look_for": ("button", {"class": "selectable-button"}),
    "wait_for": "location-select-input",
}

# Variable constants
# needs to be changed in Docker container
APP_PATH = "/home/sam/Documenten/Workspace/matchboxd"
DATABASE = "database/database.sqlite"
LETTERBOXD_JSON_URL = "https://letterboxd-list-radarr.onrender.com/"
MODE = "local"
LOCATIONS_WEB_FILE = "web/data/cities.json"
LB_LIST_FILE = "web/data/lb_list.json"
WEB_FILE = "web/data/films_with_showings.json"
