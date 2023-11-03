import sqlite3

def db_conn(db):
    conn = sqlite3.connect(db)
    return conn

def db_close(conn):
    conn.commit()
    conn.close()

def db_init(db):

    conn = db_conn(db)
    cursor = conn.cursor()

    # Create a table to store the films data
    cursor.execute('''
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
    ''')

    # Create a table to store the showings data
    cursor.execute('''
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
    ''')

    # Commit the changes and close the connection
    db_close(conn)

def db_add_cv_films(data, db):
    conn = db_conn(db)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM films")
    conn.commit()

    for film in data:
        cursor.execute('''
            INSERT INTO films
            (title, url, screening_state, oneliner, img_url)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            film['title'],
            film['url'],
            film['screening_state'],
            film['oneliner'],
            film['img_url']
        ))

    # Commit the changes and close the connection
    db_close(conn)

def db_add_cv_films_tmdb(data, db):
    conn = db_conn(db)
    cursor = conn.cursor()

    for film in data:
        cursor.execute("SELECT * FROM films WHERE title=?", (film['title'],))
        db_film = cursor.fetchone()
        if db_film is not None:
            cursor.execute("UPDATE films SET tmdb_id=? WHERE title=?", (film['tmdb_id'], film['title']))
            print(f"Updated tmdb_id for movie '{film['title']}' to {film['tmdb_id']}")
        else:
            print(f"Movie with title '{film['title']}' not found.")

    # Commit the changes and close the connection
    db_close(conn)


def db_add_lb_films(data, db):
    conn = db_conn(db)
    cursor = conn.cursor()

    for film in data:
        cursor.execute("SELECT * FROM films WHERE tmdb_id=?", (film['tmdb_id'],))
        db_film = cursor.fetchone()
        if db_film is not None:
            cursor.execute("UPDATE films SET lb_url=? WHERE tmdb_id=?", (film['url'], film['tmdb_id']))
            cursor.execute("UPDATE films SET lb_title=? WHERE tmdb_id=?", (film['title'], film['tmdb_id']))
            cursor.execute("UPDATE films SET imdb_id=? WHERE tmdb_id=?", (film['imdb_id'], film['tmdb_id']))
            cursor.execute("UPDATE films SET adult=? WHERE tmdb_id=?", (film['adult'], film['tmdb_id']))
            cursor.execute("UPDATE films SET lb_check=? WHERE tmdb_id=?", (film['lb_check'], film['tmdb_id']))
            cursor.execute("UPDATE films SET release_year=? WHERE tmdb_id=?", (film['release_year'], film['tmdb_id']))
            print(f"Added data to film '{film['title']}'.")
        else:
            print(f"Movie with title '{film['title']}' not found.")

    # Commit the changes and close the connection
    db_close(conn)

def db_add_showings(data, db):
    conn = db_conn(db)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM showings")
    conn.commit()

    for film in data:
        for showing in film['showings']:
            cursor.execute('''
            INSERT INTO showings
            (tmdb_id, date, time_start, time_end, location_name, location_city, show_title, ticket_url, information_url, screening_info, additional_info)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                film['tmdb_id'],
                showing['date'],
                showing['time_start'],
                showing['time_end'],
                showing['location_name'],
                showing['location_city'],
                showing['show_title'],
                showing['ticket_url'],
                showing['information_url'],
                showing['screening_info'],
                showing['additional_info']
            ))

    # Commit the changes and close the connection
    db_close(conn)
