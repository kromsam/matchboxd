import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import time
import datetime
from json import JSONEncoder

class DateEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.date):
            return obj.isoformat()
        return super().default(obj)

def convert_day_to_date(day_str):
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
    english_day = day_mapping.get(day_str, day_str)  # Get English day name or keep it as is
    today = datetime.date.today()  # Get today's date
    if english_day == "today":
        return today
    if english_day == "tomorrow":
        return today + datetime.timedelta(days=1)
    # Handle other days
    for i in range(2, 9):  # Check the next 7 days
        if (today + datetime.timedelta(days=i)).strftime('%A').lower() == english_day:
            return today + datetime.timedelta(days=i)
    else:
        # Extract the date string (assuming it's in the format "day day_number month")
        parts = day_str.split()
        if len(parts) == 3:
            day_number = int(parts[1])
            month_name = parts[2]
            month_number = {
                "januari": 1, "februari": 2, "maart": 3, "april": 4,
                "mei": 5, "juni": 6, "juli": 7, "augustus": 8,
                "september": 9, "oktober": 10, "november": 11, "december": 12
            }[month_name]
            current_year = today.year
            new_date = datetime.date(current_year, month_number, day_number)
            if new_date < today:
                new_date = datetime.date(current_year + 1, month_number, day_number)
            return new_date
        else:
            return None

# Specify the path to the GeckoDriver executable
driver_path = 'GeckoDriver/geckodriver'  # Replace with the actual path

# Create a FirefoxOptions instance
firefox_options = Options()

# Set the path to the GeckoDriver executable
firefox_options.binary_location = driver_path

# Initialize the Firefox web driver with the custom options
driver = webdriver.Firefox(options=firefox_options)

# Load the JSON data from your file
with open('output/common_films.json', 'r') as file:
    film_data = json.load(file)

# Iterate over each film in the JSON data and add showings
for film in film_data:
    # Get the URL for the current film
    cv_film_url = film['url']

    # Navigate to the webpage
    url = cv_film_url
    driver.get(url)

    # Wait for the page to load completely (you may need to adjust the wait time)
    driver.implicitly_wait(10)

    # Use WebDriverWait to wait for elements to load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "film-draaitijden")))
    
    # Decline cookies
    try:
        cookie_decline = driver.find_element(By.ID, "CybotCookiebotDialogBodyButtonDecline")
        cookie_decline.click()
    except NoSuchElementException:
        print("Cookie consent element not found. Continuing without interaction.")

    expand_button = driver.find_element(By.CLASS_NAME,'agenda-filters__row--cities')
    expand_button.click()

    # Get user input for locations to expand (line-separated)
    locations_file = "input/locations.txt"
    with open(locations_file, 'r') as file:
        # Read the file line by line and strip each line
        locations = [location.strip() for location in file]

    if "all" in locations:
        # Optionally, you can also add a button to collapse all locations if needed
        pass
    else:
        # Iterate through the specified locations and click the corresponding buttons
        for location in locations:
            location_button = driver.find_element(By.XPATH, f"//button[@data-value='{location}']")
            location_button_classes = location_button.get_attribute("class")

    if "selectable-button--selected" not in location_button_classes:
        location_button.click()

    # Give the page some time to load after button interactions
    time.sleep(5)

    # Get the page source
    page_source = driver.page_source

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(page_source, 'html.parser')
    # Add showings to the film data
    showings = []

    day_groups = soup.find_all(class_="shows-list__day-group")
    if day_groups:
        for day_group in day_groups:
            date = convert_day_to_date(day_group.find(class_="shows-list__day").text)
            shows = day_group.find_all(class_="shows-list-item--compact")

            for show in shows:
                time_start = show.find(class_="shows-list-item__time__start").text
                time_end = show.find(class_="shows-list-item__time__end").text
                location_name = show.find(class_="shows-list-item__location__name").text
                location_city = show.find(class_="shows-list-item__location__city").text
                show_title = show.find(class_="shows-list-item__title").text
                
                # Extract ticket_url and information_url
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
                    "screening_info": None
                }

                # Check for the presence of additional information
                additional_info = show.find("div", class_="shows-list-item__tags")
                if additional_info:
                    show_info["additional_info"] = additional_info.get_text(strip=True)
                else:
                    show_info["additional_info"] = None

                showings.append(show_info)
    else:
        screening_info = soup.select_one('.shows-list__screening-info h3').text
        show_info = {
            "date": None,
            "time_start": None,
            "time_end": None,
            "location_name": None,
            "location_city": None,
            "show_title": None,
            "ticket_url": None,
            "information_url": None,
            "screening_info": screening_info,
            "additional_info": None
        }
        showings.append(show_info)
    
    # Add the showings to the film data
    film['showings'] = showings

# Save the updated film data to a new JSON file
with open('web/films_with_showings.json', 'w') as json_file:
    json.dump(film_data, json_file, indent=4, cls=DateEncoder)

print("Showings have been added to the films and saved to films_with_showings.json.")

# Close the Selenium driver
driver.quit()