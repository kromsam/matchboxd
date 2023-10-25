import json
import requests

# Replace 'YOUR_API_KEY' with your actual TMDb API key
API_KEY = '5f97bf51209831a0c436859e0f8ec07e'

# Load the list of films from the JSON file
with open('output/cv_films_raw.json', 'r') as file:
    films = json.load(file)

def get_movie_id(movie_title):
    base_url = "https://api.themoviedb.org/3/search/movie"
    params = {
        "api_key": API_KEY,
        "query": movie_title
    }
    response = requests.get(base_url, params=params)
    data = response.json()
    if data.get('results'):
        return data['results'][0]['id']
    return None

# Add TMDb IDs to the films
for film in films:
    movie_title = film["title"]
    movie_id = get_movie_id(movie_title)
    film["tmdb_id"] = movie_id

# Save the updated JSON back to the file
with open('output/cv_films.json', 'w') as file:
    json.dump(films, file, indent=4)

print("TMDb IDs added to films and saved to cv_films_with_tmdb_id.json")