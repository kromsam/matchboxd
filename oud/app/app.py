"""Module that runs Flask app for CV<3LB."""
from flask import Flask, render_template, request, jsonify
from flask import url_for

from utils.utils import load_json_data

app = Flask(__name__, template_folder="app/templates", static_folder="app/static")


@app.route("/<user>/<user_list>")
def show_page(user, user_list):
    city = request.args.get("city")
    json_param = request.args.get("json")
    city_json = request.args.get("city_json")
    script = url_for("static", filename="script.js")
    style = url_for("static", filename="style.css")

    if json_param == "true":
        # If 'json' parameter is 'true', serve the JSON data
        try:
            data = load_json_data("app/static/films_with_showings.json")
            return jsonify(data)
        except FileNotFoundError:
            return "JSON file not found", 404
    if city_json == "true":
        # If 'json' parameter is 'true', serve the JSON data
        try:
            data = load_json_data("app/static/cities.json")
            return jsonify(data)
        except FileNotFoundError:
            return "JSON file not found", 404

    return render_template(
        "index.html",
        user=user,
        user_list=user_list,
        city=city,
        script=script,
        style=style,
    )


if __name__ == "__main__":
    app.run(debug=True)
