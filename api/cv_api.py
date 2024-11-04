"""Module to handle imports from the Cineville database."""

from datetime import datetime

from .cv_api_helpers import format_city_name
from .models import City, Film, Showing


def get_film_dict(data):
    """Extract film information from the data."""
    film_dict = {}
    film_dict["title"] = data.get("title")
    film_dict["slug"] = data.get("slug")
    film_dict["screening_state"] = None
    film_dict["oneliner"] = data.get("localizableAttributes", {}).get("shortDescription")
    assets = data.get("assets", {})
    cover = assets.get("cover", {})
    film_dict["img_url"] = cover.get("url") if cover else None
    return film_dict


def get_new_showing(showing_dict, film):
    """Generate a new showing object."""
    # Showing not in the database, add it
    new_showing = Showing(**showing_dict)

    # Set the film_id to the id of the associated Film
    new_showing.film_id = film.id if film else None

    return new_showing


def get_showing_dict(data):
    """Get a dictionary with showing data from API data."""
    showing_dict = {}
    showing_dict["start_date"] = data["startDate"]
    showing_dict["end_date"] = data["endDate"]
    showing_dict["location_name"] = data["_embedded"]["venue"].get("name")
    showing_dict["location_city"] = data["_embedded"]["venue"]["address"].get("city")
    showing_dict["ticket_url"] = data["ticketingUrl"]
    showing_dict["information_url"] = data["_embedded"]["venue"]["attributes"]["website"]
    showing_dict["screening_info"] = data.get("attributes", {}).get("shortDescription")
    showing_dict["additional_info"] = data.get("localizableAttributes", {}).get("nl-NL", {}).get("shortDescription")
    return showing_dict


def import_cities_to_db(session, api_data, country):
    """Import cities from the API."""
    updated_cities = []

    for city in api_data["collections"]:
        city_slug = city.get("id")
        city_name = format_city_name(city_slug)
        timestamp = datetime.now()

        city = session.query(City).filter_by(city_slug=city_slug).first()

        if city is None:
            # Showing not in the database, add it
            new_city = City(
                city_slug=city_slug,
                city_name=city_name,
                country=country,
                timestamp=timestamp,
            )

            session.add(new_city)
            updated_cities.append(city_slug)

    session.commit()
    return updated_cities


def import_events_to_db(session, api_data, city=None):
    """Import films and showings from an events request."""
    updated_showings = []
    updated_film_titles = []
    if city:
        city = [session.query(City).filter_by(city_slug=city).first()]
    else:
        city = []

    # Add missing films
    for event in api_data["events"]:
        cv_film_id = event.get("productionId")

        # Fetching tmdb_id and Film instance from the associated film in the films table
        film = session.query(Film).filter_by(cv_film_id=cv_film_id).first()
        if film is None:
            production = event.get("_embedded", {}).get("production", {})
            film_dict = get_film_dict(production)
            film_dict["cv_film_id"] = cv_film_id
            # Film is not in database, add it
            new_film = Film(**film_dict)
            session.add(new_film)
            updated_film_titles.append(film_dict["title"])
        else:
            print(f"Film with cv_film_id {cv_film_id} already exists.")
    session.flush()  # Ensure the session is aware of the new films

    # Add showings
    for event in api_data["events"]:
        showing_dict = get_showing_dict(event)
        showing_dict["cv_showing_id"] = event.get("id")
        cv_film_id = event.get("productionId")

        # Ensure start_date and end_date are properly formatted
        showing_dict["start_date"] = format_timestamp(showing_dict.get("start_date"))
        showing_dict["end_date"] = format_timestamp(showing_dict.get("end_date"))

        film = session.query(Film).filter_by(cv_film_id=cv_film_id).first()
        showing = (
            session.query(Showing)
            .filter_by(cv_showing_id=showing_dict["cv_showing_id"])
            .first()
        )

        if showing:
            # Showing already in the database, update if necessary
            update_showing(showing, film, showing_dict)
        else:
            new_showing = get_new_showing(showing_dict, film)
            session.add(new_showing)
            updated_showings.append(showing_dict["cv_showing_id"])

    session.commit()
    return updated_showings, updated_film_titles


def format_timestamp(timestamp):
    """Format the timestamp to a proper string format."""
    if timestamp and isinstance(timestamp, str):
        try:
            return datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.000Z")
        except ValueError:
            return None
    return None


def import_productions_to_db(session, api_data, city=None):
    """Import films from a production request."""
    updated_film_titles = []
    cities = session.query(City).filter_by(city_slug=city).first()

    for data in api_data["productions"]:
        film_dict = get_film_dict(data)
        film_dict["cv_film_id"] = data.get("id")
        film_dict["cities"] = []
        if cities:
            film_dict["cities"] = [cities]
        film = session.query(Film).filter_by(cv_film_id=film_dict["cv_film_id"]).first()

        if film:
            # Film already in the database, update if necessary
            update_film(film, film_dict, updated_film_titles)
        else:
            # Film is not in database, add it
            new_film = Film(**film_dict)
            session.add(new_film)
            updated_film_titles.append(film_dict["title"])

    session.commit()
    return updated_film_titles


def remove_films(session, api_data, city):
    """Remove films that are not in the API data."""
    for film in session.query(Film).all():
        condition_met = film.cv_film_id not in [
            data.get("id") for data in api_data["productions"]
        ]

        if city is None and condition_met:
            session.delete(film)
        elif city and condition_met and city in film.cities:
            film.cities.remove(city)
            if len(film.cities) == 0:
                session.delete(film)
    session.commit()


def remove_showings(session, api_data):
    """Remove showings that are not in the API data."""
    for showing in session.query(Showing).all():
        condition_met = showing.cv_showing_id not in [
            event["id"] for event in api_data["events"]
        ]
        if condition_met:
            session.delete(showing)
    session.commit()


def update_film(film, film_dict, updated_film_titles):
    """Update film data if it has changed."""
    if film.title != film_dict["title"]:
        updated_film_titles.append(film_dict["title"])
        film.title = film_dict["title"]

    film.slug = film_dict["slug"] if film.slug != film_dict["slug"] else film.slug

    film.screening_state = (
        film_dict["screening_state"]
        if film.screening_state != film_dict["screening_state"]
        else film.screening_state
    )

    film.oneliner = (
        film_dict["oneliner"]
        if film.oneliner != film_dict["oneliner"]
        else film.oneliner
    )

    film.img_url = (
        film_dict["img_url"] if film.img_url != film_dict["img_url"] else film.img_url
    )

    # Check if the queried city is in the 'cities' list
    if film_dict["cities"] is not None:
        if film_dict["cities"] not in film.cities:
            film.cities = film.cities + film_dict["cities"]
            film.cities = list(filter(lambda x: x is not None, film.cities))


def update_showing(showing, film, showing_dict):
    """Update showing data if it has changed."""
    showing.start_date = (
        showing_dict["start_date"]
        if showing.start_date != showing_dict["start_date"]
        else showing.start_date
    )

    showing.end_date = (
        showing_dict["end_date"]
        if showing.end_date != showing_dict["end_date"]
        else showing.end_date
    )

    showing.location_name = (
        showing_dict["location_name"]
        if showing.location_name != showing_dict["location_name"]
        else showing.location_name
    )

    showing.location_city = (
        showing_dict["location_city"]
        if showing.location_city != showing_dict["location_city"]
        else showing.location_city
    )

    showing.ticket_url = (
        showing_dict["ticket_url"]
        if showing.ticket_url != showing_dict["location_city"]
        else showing.ticket_url
    )

    showing.information_url = (
        showing_dict["information_url"]
        if showing.information_url != showing_dict["information_url"]
        else showing.information_url
    )

    showing.screening_info = (
        showing_dict["screening_info"]
        if showing.screening_info != showing_dict["screening_info"]
        else showing.screening_info
    )

    showing.additional_info = (
        showing_dict["additional_info"]
        if showing.additional_info != showing_dict["additional_info"]
        else showing.additional_info
    )

    showing.film_id = film.id if showing.film_id != film.id else showing.film_id
