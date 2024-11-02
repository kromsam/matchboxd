"""Module to import a Letterboxd-list as json-data."""

import json
import logging

import requests

# Import root logger
logger = logging.getLogger(__name__)


def get_letterboxd_data(lb_list, lb_url):
    """Get data from Letterboxd list in json format"""
    online_json_url = lb_url + lb_list

    try:
        # Fetch data from the online JSON file
        logger.debug("Waiting for %s response...", online_json_url)
        response = requests.get(online_json_url, timeout=20)
        logger.debug("%s responded.", {online_json_url})

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            logger.info("Request to Letterboxd API was successful.")
            # Parse the JSON data
            online_data = response.json()

            # Modify "id" to "tmdb_id"
            for item in online_data:
                item["tmdb_id"] = item.pop("id")
                item["url"] = "https://letterboxd.com" + item.pop("clean_title")
                item["lb_check"] = True

            return online_data
        logger.error(
            "Failed to fetch data from %s. "
            "Status: %s", online_json_url, response.status_code
        )
        return None

    except requests.exceptions.RequestException as e:
        logger.error("An error occurred while trying to fetch data: %s ", e)
        return None
    except json.JSONDecodeError as e:
        logger.error("Failed to parse the JSON data: %s", e)
        return None
