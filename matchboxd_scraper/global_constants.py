"""Global variables for matchboxd_scraper"""

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
