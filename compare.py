import json

# Load the contents of the two JSON files
with open('output/cv_films.json', 'r') as cv_file:
    cv_films_data = json.load(cv_file)

with open('output/lb_films.json', 'r') as lb_file:
    lb_films_data = json.load(lb_file)

# Create a dictionary to store films with matching tmdb_id
common_films = {}

# Iterate through cv_films to find common films
for cv_film in cv_films_data:
    tmdb_id = cv_film.get('tmdb_id')
    lb_film = next((film for film in lb_films_data if film.get('tmdb_id') == tmdb_id), None)
    
    if lb_film:
        # Create a new dictionary with the merged data
        merged_film = {
            "title": cv_film.get('title'),
            "tmdb_id": tmdb_id,
            "url": cv_film.get('url'),
            "screening_state": cv_film.get('screening_state'),
            "oneliner": cv_film.get('oneliner'),
            "img_url": cv_film.get('img_url'),
            "imdb_id": lb_film.get('imdb_id'),
            "lb_title": lb_film.get('title'),
            "release_year": lb_film.get('release_year'),
            "adult": lb_film.get('adult'),
            "lb_url": lb_film.get('url')
        }
        
        common_films[tmdb_id] = merged_film

# Save the common films to a new JSON file
with open('output/common_films.json', 'w') as common_file:
    json.dump(list(common_films.values()), common_file, indent=4)

print("Common films have been saved to 'common_films.json'")