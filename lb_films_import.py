import requests
import json

# Replace the URL with the URL of the online JSON file you want to import
LETTERBOXD_JSON_URL = "https://letterboxd-list-radarr.onrender.com/"
with open('input/letterboxd_list.txt', 'r') as file:
    # Read the entire contents of the file
    letterboxd_list = file.read()

online_json_url = LETTERBOXD_JSON_URL + letterboxd_list

try:
    # Fetch data from the online JSON file
    response = requests.get(online_json_url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the JSON data
        online_data = response.json()

        # Modify "id" to "tmdb_id"
        for item in online_data:
            item["tmdb_id"] = item.pop("id")
            item["url"] = "https://letterboxd.com" + item.pop("clean_title")

        # Define the local file path to save the imported data
        local_file_path = "output/lb_films.json"

        # Save the imported data to a local JSON file
        with open(local_file_path, "w") as json_file:
            json.dump(online_data, json_file, indent=4)

        print(f"Data from {online_json_url} has been successfully imported and saved to {local_file_path}.")

    else:
        print(f"Failed to fetch data from {online_json_url}. Status code: {response.status_code}")

except requests.exceptions.RequestException as e:
    print(f"An error occurred while trying to fetch data: {e}")
except json.JSONDecodeError as e:
    print(f"Failed to parse the JSON data: {e}")
except Exception as e:
    print(f"An error occurred: {e}")