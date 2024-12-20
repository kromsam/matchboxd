"""Module providing json-data of filmpage in Cineville."""

import datetime
import logging
from dataclasses import dataclass
from typing import List, Any

from .db_utils import load_db_data
from .utils import get_cv_data, get_html_element


# Import root logger
logger = logging.getLogger(__name__)


def convert_day_to_date(day_str):
    """returns a date from a dutch day name"""
    # Define a mapping of Dutch day names to English day names
    day_mapping = {
        "vandaag": "today",
        "morgen": "tomorrow",
        "maandag": "monday",
        "dinsdag": "tuesday",
        "woensdag": "wednesday",
        "donderdag": "thursday",
        "vrijdag": "friday",
        "zaterdag": "saturday",
        "zondag": "sunday",
    }
    english_day = day_mapping.get(
        day_str, day_str
    )  # Get English day name or keep it as is
    today = datetime.date.today()  # Get today's date
    if english_day == "today":
        return today
    if english_day == "tomorrow":
        return today + datetime.timedelta(days=1)
    # Handle other days
    for i in range(2, 9):  # Check the next 7 days
        if (today + datetime.timedelta(days=i)).strftime("%A").lower() == english_day:
            return today + datetime.timedelta(days=i)
    # Extract the date string (assuming it's in the format "day day_number month")
    parts = day_str.split()
    if len(parts) == 3:
        day_number = int(parts[1])
        month_name = parts[2]
        month_number = {
            "januari": 1,
            "februari": 2,
            "maart": 3,
            "april": 4,
            "mei": 5,
            "juni": 6,
            "juli": 7,
            "augustus": 8,
            "september": 9,
            "oktober": 10,
            "november": 11,
            "december": 12,
        }[month_name]
        current_year = today.year
        new_date = datetime.date(current_year, month_number, day_number)
        if new_date < today:
            new_date = datetime.date(current_year + 1, month_number, day_number)
        return new_date
    return None


@dataclass
class ScrapeConfig:
    """Config class"""

    locations: List[str]
    elements: List[Any]
    scrape_mode: str


class ScrapeCVFilmPage:
    """Class for scraping individual film pages"""

    def __init__(self, scrape_driver, scrape_config):
        self.driver = scrape_driver
        self.config = scrape_config

    def run_scrape(self, db):
        """Run the scraping process."""
        query = self._get_query_for_mode()
        film_data = load_db_data(db, query)
        for film in film_data:
            self.import_film_showings(film)
        return film_data

    def _get_query_for_mode(self):
        """Return the SQL query based on the scrape mode."""
        if self.config.scrape_mode == "local":
            query = "SELECT * FROM films WHERE lb_check = 1"
        elif self.config.scrape_mode == "all":
            query = "SELECT * FROM films"
        else:
            logger.error("%s is not a valid scrape_mode.", self.config.scrape_mode)
            return None
        return query

    def import_film_showings(self, film):
        """Import showing data for a single film."""
        film["showings"] = get_cv_data(
            self.driver,
            film["url"],
            self._scrape_cv_film_data,
            self.config.locations,
            self.config.elements,
        )
        logger.info("Scraped data for: %s.", film["title"])
        return film

    def _scrape_cv_film_data(self, soup, look_for_element):
        """Scrape data from a Cineville film page."""
        day_groups = get_html_element(soup, look_for_element)

        if day_groups:
            return self._extract_showings_with_agenda(day_groups)
        return [self._extract_showings_without_agenda(soup)]

    def _extract_showings_with_agenda(self, day_groups):
        """Extract showings from day groups that have an agenda."""
        showings = []
        for day_group in day_groups:
            date = convert_day_to_date(day_group.find(class_="shows-list__day").text)
            shows = day_group.find_all(class_="shows-list-item--compact")

            for show in shows:
                show_info = self._construct_show_info(show, date)
                showings.append(show_info)
        return showings

    def _construct_show_info(self, show, date):
        """Construct a dictionary of show information from an individual element."""
        time_start = show.find(class_="shows-list-item__time__start").text
        time_end = show.find(class_="shows-list-item__time__end").text
        location_name = show.find(class_="shows-list-item__location__name").text
        location_city = show.find(class_="shows-list-item__location__city").text
        show_title = show.find(class_="shows-list-item__title").text
        cineville_url = "https://www.cineville.nl"
        additional_info = show.find("div", class_="shows-list-item__additional")
        ticket_link = additional_info.find("a", string="Direct reserveren")
        info_link = additional_info.find("a", string="Informatie")
        ticket_url = cineville_url + ticket_link["href"] if ticket_link else None
        information_url = cineville_url + info_link["href"] if info_link else None

        show_info = {
            "date": date,
            "time_start": time_start,
            "time_end": time_end,
            "location_name": location_name,
            "location_city": location_city,
            "show_title": show_title,
            "ticket_url": ticket_url,
            "information_url": information_url,
            "screening_info": None,
            "additional_info": self._extract_additional_info(show),
        }
        return show_info

    def _extract_additional_info(self, show):
        """Extract additional information if present."""
        additional_info_tag = show.find("div", class_="shows-list-item__tags")
        return additional_info_tag.get_text(strip=True) if additional_info_tag else None

    def _extract_showings_without_agenda(self, soup):
        """Handle showings when no agenda data is found."""
        if soup.select_one(".shows-list__screening-info h3"):
            screening_info = soup.select_one(".shows-list__screening-info h3").text
        else:
            screening_info = None

        return {
            "date": None,
            "time_start": None,
            "time_end": None,
            "location_name": None,
            "location_city": None,
            "show_title": None,
            "ticket_url": None,
            "information_url": None,
            "screening_info": screening_info,
            "additional_info": None,
        }
