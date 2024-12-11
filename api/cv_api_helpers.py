"""Helper functions for cv_api."""

from datetime import datetime, timedelta
import logging

import httpx

from api.helpers import extract_api_url

from .global_constants import CV_API, TYPE_CITIES, TYPE_EVENTS, TYPE_PRODUCTIONS

# Import the root logger
logger = logging.getLogger(__name__)


def fetch_data_from_api(base_url, endpoint, params):
    """Fetch data from the Cineville API."""
    params["page[limit]"] = 1
    response = get_api_response(base_url, endpoint, params)
    if response:
        print("Request URL: %s", response.url)
        response_data = response.json()

        # Check if the first key of the dict is "error"
        if list(response_data.keys())[0] == "error":
            error_code = response_data["error"].get("code")
            unique_identifier = response_data["error"].get(
                "unique_identifier"
            )
            raise ValueError(
                f"Error {error_code}: {unique_identifier}"
            )

        count = response_data.get("count")
        total_count = response_data.get("totalCount")
    else:
        return None

    if total_count > 1000:
        print("Total count is above 1000")
        # raise ValueError("totalCount exceeds 1000")
        # function to iterate over pages
        response_block = response_data["_embedded"]
        print(response_block)
        response_endpoint = list(response_data["_embedded"].keys())[0]
        print("Response endpoint:", response_endpoint)
        while "_links" in response_data and "next" in response_data["_links"]:
            next_page_url = base_url + response_data["_links"]["next"]["href"]
            base_url, endpoint, params = extract_api_url(next_page_url)
            params["page[limit]"] = 100
            response = get_api_response(base_url, endpoint, params)
            if response:
                response_data = response.json()

                # Check if the first key of the dict is "error"
                if list(response_data.keys())[0] == "error":
                    error_code = response_data["error"].get("code")
                    unique_identifier = response_data["error"].get(
                        "unique_identifier"
                    )
                    raise ValueError(
                        f"Error {error_code}: {unique_identifier}"
                    )

                response_block[response_endpoint].extend(
                    response_data["_embedded"][response_endpoint]
                )
                print(response_block)
            else:
                break
        return response_block
    if total_count > count:
        # Update the page limit to retrieve all results in a single page
        params["page[limit]"] = total_count
        response = get_api_response(base_url, endpoint, params)
        if response:
            response_data = response.json()
            return response_data["_embedded"]
        return None
    return response_data["_embedded"]


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
        response = httpx.get(base_url + endpoint, params=params, timeout=30)
        response.raise_for_status()  # Raise exception for 4xx & 5xx status

        return response
    except httpx.HTTPError as http_err:
        logger.error("HTTP error occurred: %s", http_err)
        return None


def get_api_url(
    query_type, country, city=None, start_date=None, page_limit=None
):
    """Generate the url for the API request to Cineville."""
    base_url = CV_API[country]
    endpoint = ""
    params = {}

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
