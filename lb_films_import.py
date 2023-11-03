"""Module to import a Letterboxd-list as json-data."""
import json

import requests

from utils import get_lb_list


def get_letterboxd_data(lb_list, lb_url):
    """Get data from Letterboxd list in json format"""
    letterboxd_list = get_lb_list(lb_list)
    online_json_url = lb_url + letterboxd_list

    try:
        # Fetch data from the online JSON file
        print(f"Waiting for {online_json_url} response...")
        response = requests.get(online_json_url, timeout=20)
        print(f"{online_json_url} responded.")

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            print("Request was succesful.")
            # Parse the JSON data
            online_data = response.json()

            # Modify "id" to "tmdb_id"
            for item in online_data:
                item["tmdb_id"] = item.pop("id")
                item["url"] = "https://letterboxd.com" + item.pop("clean_title")
                item["lb_check"] = True

            return online_data
        else:
            print(f"Failed to fetch data from {online_json_url}. Status code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while trying to fetch data: {e}")
    except json.JSONDecodeError as e:
        print(f"Failed to parse the JSON data: {e}")
