"""Module to import a Letterboxd-list as json-data."""
import json

import requests

from utils import get_lb_list
from utils import store_data

# Replace the URL with the URL of the online JSON file you want to import
LETTERBOXD_JSON_URL = "https://letterboxd-list-radarr.onrender.com/"
LB_LIST = "input/letterboxd_list.txt"
OUTPUT_FILE = "output/lb_films.json"


def get_letterboxd_data(lb_list):
    """Get data from Letterboxd list in json format"""
    letterboxd_list = get_lb_list(lb_list)
    online_json_url = LETTERBOXD_JSON_URL + letterboxd_list

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

            return online_data
        else:
            print(f"Failed to fetch data from {online_json_url}. Status code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while trying to fetch data: {e}")
    except json.JSONDecodeError as e:
        print(f"Failed to parse the JSON data: {e}")


if __name__ == "__main__":
    print(f"Fetching data from Letterboxd-list: {get_lb_list(LB_LIST)}")
    data = get_letterboxd_data(LB_LIST)
    print("Data found.")
    store_data(data, OUTPUT_FILE)
