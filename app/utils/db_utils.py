"""Database utils for Cineville Heart Letterboxd."""

import os
import sqlite3


def db_add_cv_films(data, db):
    """Add films from Cineville Films page."""
    conn = db_conn(db, "rw")
    cursor = conn.cursor()

    del_from = "films"
    db_delete(conn, cursor, del_from)

    for film in data:
        cursor.execute(
            """
            INSERT INTO films
            (title, url, screening_state, oneliner, img_url)
            VALUES (?, ?, ?, ?, ?)
        """,
            (
                film["title"],
                film["url"],
                film["screening_state"],
                film["oneliner"],
                film["img_url"],
            ),
        )

    # Commit the changes and close the connection
    db_commit_close(conn)


def db_add_cv_films_tmdb(data, db):
    """Add TMDB IDs to database."""
    conn = db_conn(db, "rw")
    cursor = conn.cursor()

    for film in data:
        cursor.execute("SELECT * FROM films WHERE title=?", (film["title"],))
        db_film = cursor.fetchone()
        if db_film is not None:
            cursor.execute(
                "UPDATE films SET tmdb_id=? WHERE title=?",
                (film["tmdb_id"], film["title"]),
            )
            print(f"Updated tmdb_id for movie '{film['title']}' to {film['tmdb_id']}")
        else:
            print(f"Movie with title '{film['title']}' not found.")

    # Commit the changes and close the connection
    db_commit_close(conn)


def db_add_lb_films(data, db):
    """Add Letterboxd films to database."""
    conn = db_conn(db, "rw")
    cursor = conn.cursor()

    for film in data:
        cursor.execute("SELECT * FROM films WHERE tmdb_id=?", (film["tmdb_id"],))
        db_film = cursor.fetchone()
        if db_film is not None:
            cursor.execute(
                "UPDATE films SET lb_url=? WHERE tmdb_id=?",
                (film["url"], film["tmdb_id"]),
            )
            cursor.execute(
                "UPDATE films SET lb_title=? WHERE tmdb_id=?",
                (film["title"], film["tmdb_id"]),
            )
            cursor.execute(
                "UPDATE films SET imdb_id=? WHERE tmdb_id=?",
                (film["imdb_id"], film["tmdb_id"]),
            )
            cursor.execute(
                "UPDATE films SET adult=? WHERE tmdb_id=?",
                (film["adult"], film["tmdb_id"]),
            )
            cursor.execute(
                "UPDATE films SET lb_check=? WHERE tmdb_id=?",
                (film["lb_check"], film["tmdb_id"]),
            )
            cursor.execute(
                "UPDATE films SET release_year=? WHERE tmdb_id=?",
                (film["release_year"], film["tmdb_id"]),
            )
            print(f"Added data to film '{film['title']}'.")
        else:
            print(f"Movie with title '{film['title']}' not found.")

    # Commit the changes and close the connection
    db_commit_close(conn)


def db_add_showings(data, db):
    """Add showings to database."""
    conn = db_conn(db, "rw")
    cursor = conn.cursor()

    del_query = "showings"
    db_delete(conn, cursor, del_query)

    for film in data:
        for showing in film["showings"]:
            cursor.execute(
                """
            INSERT INTO showings
            (
            tmdb_id,
            date,
            time_start,
            time_end,
            location_name,
            location_city,
            show_title,
            ticket_url,
            information_url,
            screening_info,
            additional_info
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    film["tmdb_id"],
                    showing["date"],
                    showing["time_start"],
                    showing["time_end"],
                    showing["location_name"],
                    showing["location_city"],
                    showing["show_title"],
                    showing["ticket_url"],
                    showing["information_url"],
                    showing["screening_info"],
                    showing["additional_info"],
                ),
            )

    # Commit the changes and close the connection
    db_commit_close(conn)


def db_conn(db, db_mode):
    """Connect to a database in a specific mode."""
    conn = sqlite3.connect(f"file:{db}?mode={db_mode}", uri=True)
    return conn


def db_commit_close(conn):
    """Commit changes and close database"""
    conn.commit()
    conn.close()


def db_init(db):
    """Initialize database."""
    # Ensure the directory exists
    os.makedirs(os.path.dirname(db), exist_ok=True)

    with open(db, "w", encoding="utf-8"):
        pass  # An empty 'pass' statement creates an empty file

    conn = db_conn(db, "rw")
    cursor = conn.cursor()

    # Create a table to store the films data
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS films (
            id INTEGER PRIMARY KEY,
            tmdb_id INTEGER,
            title TEXT,
            url TEXT,
            screening_state TEXT,
            oneliner TEXT,
            img_url TEXT,
            imdb_id TEXT,
            lb_title TEXT,
            release_year TEXT,
            adult INTEGER,
            lb_url TEXT,
            lb_check INTEGER
        )
    """
    )

    # Create a table to store the showings data
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS showings (
            id INTEGER PRIMARY KEY,
            tmdb_id INTEGER,
            date TEXT,
            time_start TEXT,
            time_end TEXT,
            location_name TEXT,
            location_city TEXT,
            show_title TEXT,
            ticket_url TEXT,
            information_url TEXT,
            screening_info TEXT,
            additional_info TEXT
        )
    """
    )

    # Commit the changes and close the connection
    db_commit_close(conn)


def db_delete(conn, cursor, del_from):
    """Delete rows from database."""
    cursor.execute(f"DELETE FROM {del_from}")
    conn.commit()


def load_db_data(db, query):
    """Load data from database in a list of dictionaries."""
    # Execute a SQL query to select films with lb_check=True
    conn = db_conn(db, "ro")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query)

    # Fetch all the rows that match the condition
    data_raw = cursor.fetchall()
    conn.close()

    data = []
    for row in data_raw:
        data.append(dict(row))
    return data
