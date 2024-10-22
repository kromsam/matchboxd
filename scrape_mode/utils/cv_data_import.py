"""Module providing json-data of filmpage in Cineville."""
import datetime

from utils.db_utils import load_db_data
from utils.utils import get_cv_data
from utils.utils import get_html_element


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
    return None


def get_cv_film_data(driver, scrape_function, locations, db, elements, scrape_mode):
    """Loop through films and get data from Cineville."""

    # Execute a SQL query to select films with lb_check=True
    if scrape_mode == "local":
        query = "SELECT * FROM films WHERE lb_check = 1"
    elif scrape_mode == "full":
        query = "SELECT * FROM films"
    film_data = load_db_data(db, query)

    # Iterate over each film in the JSON data and add showings

    for film in film_data:
        print(f"Importing data from {film['title']}...")
        film['showings'] = get_cv_data(driver, film['url'], scrape_function, locations, elements)
        print("Import succesful.")

    return film_data


def scrape_cv_film_data(soup, look_for_element):
    """Scrape data from a Cineville film page"""
    print(f"Look for {look_for_element} element...")
    day_groups = get_html_element(soup, look_for_element)
    showings = []
    if day_groups:
        print("Film data with agenda found.")
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
        if soup.select_one('.shows-list__screening-info h3'):
            print("Film data without agenda, with screening info found.")
            screening_info = soup.select_one('.shows-list__screening-info h3').text
        else:
            print("Film data without agenda and screening info found.")
            screening_info = None
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
    return showings
