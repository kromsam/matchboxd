"""Module providing a json films screening in a specific city in Cineville."""

import logging

from utils import get_html_element


# Import root logger
logger = logging.getLogger(__name__)


def extract_text(element, default="Not found"):
    """Extract text from an element or return a default value."""
    return element.text if element else default


def extract_attribute(element, attribute, default="Not found"):
    """Extract an attribute from an element or return a default value."""
    return element[attribute] if element else default


def find_oneliner(film_element, class_names):
    """Find and return the oneliner text from possible class names."""
    for class_name in class_names:
        oneliner_element = film_element.find("div", class_=class_name)
        if oneliner_element:
            return oneliner_element.text
    return "Geen informatie beschikbaar."


def format_img_url(img_element):
    """Format the image URL to remove query parameters or return a default."""
    if img_element:
        return img_element["data-src"].split("?w=")[0]
    return "Image URL not found"


def extract_film_details(film_element, oneliner_class_names):
    """Extract and return film details from a film element."""
    title_element = film_element.find("h3", class_="card__title")
    url_element = film_element.find("a", class_="block-link")
    screening_state_element = film_element.find(
        "div", class_="film-card__screening-state-text"
    )
    img_element = film_element.find("img", class_="image-replace")

    title = extract_text(title_element, "Title not found")
    url = extract_attribute(url_element, "href", "URL not found")
    full_url = f"https://www.cineville.nl{url}"
    screening_state = extract_text(
        screening_state_element, "Geen informatie beschikbaar."
    )
    oneliner = find_oneliner(film_element, oneliner_class_names)
    img_url = format_img_url(img_element)

    return {
        "title": title,
        "url": full_url,
        "screening_state": screening_state,
        "oneliner": oneliner,
        "img_url": img_url,
    }


def scrape_cv_film_list(soup, look_for):
    """Scrape Cineville for all films screening in specific cities."""
    film_elements = get_html_element(soup, look_for)
    if not film_elements:
        logger.info("No film elements found on page.")
        return []

    oneliner_class_names = ["film-card__oneliner", "film-card__film-tip-quote"]
    films = []
    for film_element in film_elements:
        film_details = extract_film_details(film_element, oneliner_class_names)
        films.append(film_details)
        logger.info("%s", film_details["title"])

    return films


def scrape_cv_location_list(soup, look_for):
    """Get all locations from Cineville films page."""
    # Find all the selectable buttons by their class name
    location_elements = get_html_element(soup, look_for)
    if location_elements:
        cities = [button.text for button in location_elements]
        return cities
    logger.info("No location elements found on page.")
    return None
