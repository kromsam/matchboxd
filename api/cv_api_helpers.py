"""Helper functions for cv_api."""

from datetime import datetime, timedelta
import logging

import httpx

from .config import CV_API
from .global_constants import TYPE_CITIES, TYPE_EVENTS, TYPE_PRODUCTIONS

# Import the root logger
logger = logging.getLogger(__name__)


def fetch_data_from_api(base_url, endpoint, params):
    """Fetch data from the Cineville API."""
    response = get_api_response(base_url, endpoint, params)
    logger.info("Request URL: %s", response.url)
    response_data = response.json()

    count = response_data.get("count")
    total_count = response_data.get("totalCount")

    if total_count > 1000:
        raise ValueError("totalCount exceeds 1000")
    if total_count > count:
        # Update the page limit to retrieve all results in a single page
        params["page[limit]"] = total_count
        response = get_api_response(base_url, endpoint, params)
        response_data = response.json()
    return response_data


def format_city_name(name):
    """Format the name of cities from their slug."""
    # Custom function to format city names
    parts = name.split("-")
    formatted_name = " ".join(
        part.capitalize() if not part.startswith("ij") else "IJ" + part[2:]
        for part in parts
    )
    return formatted_name


def get_api_response(base_url, endpoint, params):
    """Make an API request."""
    try:
        response = httpx.get(base_url + endpoint, params=params, timeout=20)
        response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes
        return response
    except httpx.HTTPError as http_err:
        logger.error("HTTP error occurred: %s", http_err)


def get_api_url(query_type, country, city=None, start_date=None, page_limit=None):
    """Generate the url for the API request to Cineville."""
    base_url = CV_API[country]

    if query_type == TYPE_PRODUCTIONS:
        endpoint = "/productions"
        params = {"collection[common][in][0]": "now-screening"}

    if query_type == TYPE_CITIES:
        endpoint = "/collections"
        params = {"collectionGroupId[in][0]": "cities"}

    if query_type == TYPE_EVENTS:
        endpoint = "/events"
        params = {"embed[venue]": "true", "embed[production]": "true"}

    if city is not None:
        params["collection[cities][in][0]"] = city

    if start_date is not None:
        params["startDate[gte]"] = start_date

    if page_limit is not None:
        params["page[limit]"] = page_limit

    return base_url, endpoint, params


def get_start_date(hours_delta=0):
    """Generate a time and date to from which to start looking for showings."""
    # Get the current UTC time
    current_time = datetime.utcnow()

    # Calculate the time x hours ago
    new_time = current_time - timedelta(hours=hours_delta)

    # Format the time in ISO 8601 format
    return new_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
