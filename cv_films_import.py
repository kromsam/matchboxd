import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import time

# Specify the path to the GeckoDriver executable
driver_path = 'GeckoDriver/geckodriver'  # Replace with the actual path

# Create a FirefoxOptions instance
firefox_options = Options()

# Add the headless option
firefox_options.add_argument("-headless")

# Set the path to the GeckoDriver executable
firefox_options.binary_location = driver_path

# Initialize the Firefox web driver with the custom options
driver = webdriver.Firefox(options=firefox_options)

# Navigate to the webpage
url = "https://cineville.nl/films"  # Replace with the actual URL
driver.get(url)

try:
    # Use WebDriverWait to wait for elements to load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "all-films-list__list")))
   
   # Decline cookies
    try:
        cookie_decline = driver.find_element(By.ID, "CybotCookiebotDialogBodyButtonDecline")
        cookie_decline.click()
    except NoSuchElementException:
        print("Cookie consent element not found. Continuing without interaction.")

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
            location_button.click()

    # Give the page some time to load after button interactions
    time.sleep(2)

    # Retrieve the HTML content after the page has loaded
    html = driver.page_source

    # Parse the HTML using BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')

    # Find all the film elements within the page
    film_elements = soup.find_all('li', {'data-colspan': '1'})

    if film_elements:
        # Initialize a list to store film data
        films = []

        # Loop through the film elements to extract data
        for film_element in film_elements:
            title_element = film_element.find('h3', class_='card__title')
            url_element = film_element.find('a', class_='block-link')
            screening_state_element = film_element.find('div', class_='film-card__screening-state-text')

            # List of possible class names for the oneliner element
            oneliner_class_names = ['film-card__oneliner', 'film-card__film-tip-quote']

            # Initialize oneliner as None
            oneliner = None

            # Loop through the possible class names and find the oneliner
            for class_name in oneliner_class_names:
                oneliner_element = film_element.find('div', class_=class_name)
                if oneliner_element:
                    oneliner = oneliner_element.text
                    break  # Break out of the loop if the oneliner is found

            img_element = film_element.find('img', class_='image-replace')

            # Check if elements were found before accessing their text or attributes
            title = title_element.text if title_element else "Title not found"
            url = url_element['href'] if url_element else "URL not found"

            # Concatenate the domain to the extracted URL
            full_url = f"https://www.cineville.nl{url}"

            screening_state = screening_state_element.text if screening_state_element else "Screening state not found"
            oneliner = oneliner if oneliner else "Oneliner not found"

            # Modify the image URL to remove the ?w={width} part
            img_url = img_element['data-src'].split('?w=')[0] if img_element else "Image URL not found"

            films.append({
                "title": title,
                "url": full_url,
                "screening_state": screening_state,
                "oneliner": oneliner,
                "img_url": img_url
            })

        # Save the film data to a JSON file
        with open('output/cv_films_raw.json', 'w', encoding='utf-8') as json_file:
            json.dump(films, json_file, ensure_ascii=False, indent=4)

    else:
        print("No film elements found on the page.")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Close the Selenium driver
    driver.quit()