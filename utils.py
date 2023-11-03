"""Utils for Cineville Heart Letterboxd."""
import datetime
import json
from json import JSONEncoder
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.firefox import GeckoDriverManager


class DateEncoder(JSONEncoder):
    """Class for date conversion"""
    def default(self, o):
        if isinstance(o, datetime.date):
            return o.isoformat()
        return super().default(o)


def click_cv_location_list(location_file, driver):
    """Click through location on Cineville-webpage."""

    # Get user input for locations to expand (line-separated)
    with open(location_file, 'r', encoding="utf-8") as file:
        # Read the file line by line and strip each line
        locations = [location.strip() for location in file]
    print("Loaded locations from input file.")

    # Check for buttons to be clicked
    if "all" in locations:
        # Optionally, you can also add a button to collapse all locations if needed
        print("All locations selected, no buttons to be clicked.")
    else:
        # Iterate through the specified locations and click the corresponding buttons
        for location in locations:
            location_button = driver.find_element(By.XPATH, f"//button[@data-value='{location}']")
            location_button_classes = location_button.get_attribute("class")

            # Click buttons
            if "selectable-button--selected" not in location_button_classes:
                location_button.click()
                print(f"Clicked {location} button.")
        print("All location buttons clicked.")


def cv_class_wait(driver, wait_for_class):
    """Wait for a class on the page to load."""

    # Wait for specific class
    print(f"Waiting for {wait_for_class} to load...")
    wait_for = (By.CLASS_NAME, wait_for_class)
    driver.implicitly_wait(2)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(wait_for))
    print(f"{wait_for_class} has loaded succesfully.")


def decline_cv_cookies(driver):
    """Decline cookies on Cineville-webpage."""
    print("Declining cookies...")
    try:
        cookie_decline = driver.find_element(By.ID, "CybotCookiebotDialogBodyButtonDecline")
        cookie_decline.click()
        print("Cookies declined.")
    except NoSuchElementException:
        print("Cookie consent element not found. Continuing without interaction.")


def get_cv_data(driver, url, scrape_function, locations, wait_for_class, look_for_element):
    """Scrape Cineville for all films screening in specific cities."""

    # Go to url
    print(f"Loading webpage: {url}...")
    driver.get(url)
    print("Page loaded.")

    # Use WebDriverWait to wait for elements to load
    cv_class_wait(driver, wait_for_class)

    # Decline cookies
    decline_cv_cookies(driver)

    # Sleep after cookie interactions.
    print("Waiting for page to load after cookie interactions.")
    time.sleep(2)

    # Select locations
    click_cv_location_list(locations, driver)

    # Give the page some time to load after button interactions
    print("Waiting for page to load after location interactions.")
    time.sleep(2)

    # Scrape Cineville Films
    soup = get_html_soup(driver)

    print("Scraping data from webpage...")
    data = scrape_function(soup, look_for_element)
    print("Webpage succesfully scraped.")
    return data


def get_html_element(soup, look_for_element):
    """Find specific element in HTML-soup."""
    print(f"Looking for {look_for_element} on webpage.")
    look_for_tag, look_for_attribute = look_for_element
    film_elements = soup.find_all(look_for_tag, look_for_attribute)
    print("HTML element found.")
    return film_elements


def get_html_soup(driver):
    """Parse content of site with BeautifulSoup."""

    print("Fetching parsed html from webpage...")
    # Retrieve the HTML content after the page has loaded
    html = driver.page_source
    # Parse the HTML using BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    print("Parsed html of webpage fetched.")
    return soup


def get_lb_list(input_file):
    """Load name of letterboxd list"""
    print(f"Getting name of Letterboxd-list from {input_file}...")
    with open(input_file, 'r', encoding="utf-8") as file:
        # Read the entire contents of the file
        lb_list = file.read().strip()
    print(f"Found name: {lb_list}.")
    return lb_list


def load_json_data(input_file):
    """Load json data from a file"""
    print(f"Loading JSON-data from: {input_file}...")
    # Load the JSON data from your file
    with open(input_file, 'r', encoding='utf-8') as file:
        json_data = json.load(file)
    print("Succesfully loaded data.")
    return json_data


def run_driver():
    """Initialize a headless Firefox webdriver"""
    # Create a FirefoxOptions instance
    firefox_options = webdriver.FirefoxOptions()

    # Add the headless option
    firefox_options.add_argument("-headless")

    # Install Gecko Driver
    print("Installing Gecko Driver...")
    driver_file = GeckoDriverManager().install()
    print("Gecko Driver installed.")

    # Initialize the Firefox web driver with the custom options
    print("Initializing WebDriver...")
    driver = webdriver.Firefox(service=FirefoxService(driver_file), options=firefox_options)
    print("WebDriver initialized.")

    return driver


def store_data(data, output_file):
    """Store data to a json file."""
    print(f"Storing data in json format to: {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4, cls=DateEncoder)
    print("Data succesfully saved.")
