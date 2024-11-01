"""Module providing a json films screening in a specific city in Cineville."""

from utils import get_html_element


def scrape_cv_film_list(soup, look_for):
    """Scrape Cineville for all films screening in specific cities."""
    film_elements = get_html_element(soup, look_for)
    if film_elements:
        # Initialize a list to store film data
        films = []

        # Loop through the film elements to extract data
        for film_element in film_elements:
            title_element = film_element.find("h3", class_="card__title")
            url_element = film_element.find("a", class_="block-link")
            screening_state_element = film_element.find(
                "div", class_="film-card__screening-state-text"
            )

            # List of possible class names for the oneliner element
            oneliner_class_names = ["film-card__oneliner", "film-card__film-tip-quote"]

            # Loop through the possible class names and find the oneliner
            oneliner = None
            for class_name in oneliner_class_names:
                oneliner_element = film_element.find("div", class_=class_name)
                if oneliner_element:
                    oneliner = oneliner_element.text
                    break  # Break out of the loop if the oneliner is found

            img_element = film_element.find("img", class_="image-replace")

            # Check if elements were found before accessing their text or attributes
            title = title_element.text if title_element else "Title not found"
            url = url_element["href"] if url_element else "URL not found"

            # Concatenate the domain to the extracted URL
            full_url = f"https://www.cineville.nl{url}"

            screening_state = (
                screening_state_element.text
                if screening_state_element
                else "Geen informatie beschikbaar."
            )
            oneliner = oneliner if oneliner else "Geen informatie beschikbaar."

            # Modify the image URL to remove the ?w={width} part
            img_url = (
                img_element["data-src"].split("?w=")[0]
                if img_element
                else "Image URL not found"
            )

            films.append(
                {
                    "title": title,
                    "url": full_url,
                    "screening_state": screening_state,
                    "oneliner": oneliner,
                    "img_url": img_url,
                }
            )

            print(title + " found.")
        return films
    print("No film elements found on page.")
    return


def scrape_cv_location_list(soup, look_for):
    """Get all locations from Cineville films page."""
    # Find all the selectable buttons by their class name
    location_elements = get_html_element(soup, look_for)
    if location_elements:
        cities = [button.text for button in location_elements]
        return cities
    print("No location elements found on page.")
    return
