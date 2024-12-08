"""Utils for Cineville Heart Letterboxd."""

import datetime
import json
import time
from json import JSONEncoder
import logging

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementNotInteractableException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


# Import root logger
logger = logging.getLogger(__name__)


class DateEncoder(JSONEncoder):
    """Class for date conversion"""

    def default(self, o):
        if isinstance(o, datetime.date):
            return o.isoformat()
        return super().default(o)


def click_cv_location_list(locations, driver):
    """Click through location on Cineville-webpage."""

    # Check for buttons to be clicked
    if "all" in locations:
        # Optionally, you can also add a button to collapse all locations if needed
        logger.debug("All locations selected, no buttons to be clicked.")
    else:
        # Iterate through the specified locations and click the corresponding buttons
        for location in locations:
            location_button = driver.find_element(
                By.XPATH, f"//button[@data-value='{location}']"
            )
            location_button_classes = location_button.get_attribute("class")

            # Click buttons
            if "selectable-button--selected" not in location_button_classes:
                location_button.click()
                logger.debug("Clicked %s button.", location)
        logger.debug("All location buttons clicked.")


def cv_class_wait(driver, wait_for):
    """Wait for a class on the page to load."""

    # Wait for specific class
    logger.debug("Waiting for %s to load...", wait_for)
    wait_for = (By.CLASS_NAME, wait_for)
    driver.implicitly_wait(2)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(wait_for))
    logger.debug("%s has loaded succesfully.", wait_for)


def decline_cv_cookies(driver):
    """Decline cookies on Cineville-webpage."""
    logger.debug("Declining cookies...")
    try:
        cookie_decline = driver.find_element(
            By.ID, "CybotCookiebotDialogBodyButtonDecline"
        )
        cookie_decline.click()
        logger.debug("Cookies declined.")
    except NoSuchElementException:
        logger.debug("Cookie consent element not found. Continuing.")
    except ElementNotInteractableException:
        logger.debug(
            """Cookie consent element could not be scrolled into view.
              Continuing without interaction."""
        )


def get_cv_data(driver, url, scrape_function, locations, elements):
    """Scrape Cineville for all films screening in specific cities."""

    # Go to url
    logger.debug("Loading: %s...", url)
    driver.get(url)
    logger.info("%s loaded.", url)

    # Use WebDriverWait to wait for elements to load
    cv_class_wait(driver, elements["wait_for"])

    # Decline cookies
    decline_cv_cookies(driver)

    # Sleep after cookie interactions.
    logger.info("Waiting for page to load after cookie interactions.")
    time.sleep(2)

    # Select locations
    click_cv_location_list(locations, driver)

    # Give the page some time to load after button interactions
    logger.info("Waiting for page to load after location interactions.")
    time.sleep(2)

    # Find the div with class using Selenium
    select_element = driver.find_element(By.CLASS_NAME, elements["wait_for"])

    # Get the inner HTML of the div
    html_content = select_element.get_attribute("innerHTML")

    # Scrape Cineville Films
    soup = get_html_soup(html_content)

    logger.info("Scraping data from webpage...")
    data = scrape_function(soup, elements["look_for"])
    logger.info("Webpage succesfully scraped.")
    return data


def get_html_element(soup, look_for_element):
    """Find specific element in HTML-soup."""
    logger.debug("Looking for %s on webpage.", look_for_element)
    look_for_tag, look_for_attribute = look_for_element
    film_elements = soup.find_all(look_for_tag, look_for_attribute)
    logger.debug("HTML element found.")
    return film_elements


def get_html_soup(html_content):
    """Parse content of site with BeautifulSoup."""

    logger.debug("Fetching parsed html from webpage...")
    # Parse the HTML using BeautifulSoup
    soup = BeautifulSoup(html_content, "html.parser")
    logger.debug("Parsed html of webpage fetched.")
    return soup


def load_list(location_string):
    """Get user input for locations to expand (comma-separated)"""
    locations = [location.strip() for location in location_string.split(",")]
    logger.debug("Loaded %s from input file.", locations)
    return locations


def load_json_data(input_file):
    """Load json data from a file"""
    logger.debug("Loading JSON-data from: %s...", input_file)
    # Load the JSON data from your file
    with open(input_file, "r", encoding="utf-8") as file:
        json_data = json.load(file)
    logger.debug("Succesfully loaded data.")
    return json_data


def run_driver():
    """Initialize a headless Firefox webdriver"""
    # Create a FirefoxOptions instance
    firefox_options = webdriver.FirefoxOptions()

    # Add the headless option
    firefox_options.add_argument("-headless")

    # Initialize the Firefox web driver with the custom options
    logger.debug("Initializing WebDriver...")
    driver = webdriver.Firefox(options=firefox_options)
    logger.info("WebDriver initialized.")

    return driver


def store_data(data, output_file):
    """Store data to a json file."""
    logger.debug("Storing data in json format to: %s...", output_file)
    with open(output_file, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4, cls=DateEncoder)
    logger.info("Data succesfully saved to %s", output_file)
