import sqlite3
import requests

DB_NAME = "final_project.db"

# Your Genius access token
GENIUS_ACCESS_TOKEN = "J2Z_IIvWZ0aF6Czx8FRUAnRXofz_GaTMh66z8xB9j56z-1lmCRQuyM4XZVWTmIq6"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    return conn, cur


def create_tables(cur):
    # One table, one row per Genius artist
    cur.execute("""
        CREATE TABLE IF NOT EXISTS GeniusArtists (
            genius_artist_id INTEGER PRIMARY KEY,
            artist_name TEXT,
            rank INTEGER
        )
    """)


def fetch_genius_artists():
    """
    Use the Genius search API to find artist IDs for a ranked list
    of top 100 artists of all time.

    Fill ARTIST_NAMES with the real 100 names in order.
    """
    ARTIST_NAMES = [
        # TODO: replace with the actual 100 names from Genius, in order
        "The Beatles",
        "Michael Jackson",
        "Madonna",
        "Elvis Presley",
        "Taylor Swift",
        # ...
    ]

    results = []
    base_url = "https://api.genius.com/search"

    for rank_index in range(len(ARTIST_NAMES)):
        name = ARTIST_NAMES[rank_index]

        # Simple URL encoding: replace spaces with %20
        query = name.replace(" ", "%20")

        url = (base_url +
               "?q=" + query +
               "&access_token=" + GENIUS_ACCESS_TOKEN)

        response = requests.get(url)
        data = response.json()

        # Walk the JSON using direct indexes/keys
        if "response" not in data:
            continue

        response_block = data["response"]
        hits = response_block["hits"]

        if len(hits) == 0:
            continue

        first_hit = hits[0]
        result_block = first_hit["result"]
        primary_artist = result_block["primary_artist"]

        artist_id = primary_artist["id"]
        artist_name = primary_artist["name"]

        artist_dict = {}
        artist_dict["genius_artist_id"] = artist_id
        artist_dict["artist_name"] = artist_name
        artist_dict["rank"] = rank_index + 1

        results.append(artist_dict)

    return results


def store_genius_data(conn, cur):
    """
    Insert up to 25 new Genius artists per run.
    Avoid duplicates with genius_artist_id.
    Stop once there are 100 rows.
    """

    cur.execute("SELECT COUNT(*) FROM GeniusArtists")
    row = cur.fetchone()
    current_count = row[0]

    if current_count >= 100:
        print("Already have 100 Genius artists. Skipping insert.")
        return

    max_new_this_run = 100 - current_count
    if max_new_this_run > 25:
        max_new_this_run = 25

    artists = fetch_genius_artists()
    inserted = 0

    for artist in artists:
        artist_id = artist["genius_artist_id"]
        artist_name = artist["artist_name"]
        rank = artist["rank"]

        # Check for duplicates
        cur.execute(
            "SELECT 1 FROM GeniusArtists WHERE genius_artist_id = ?",
            (artist_id,)
        )
        exists = cur.fetchone()
        if exists is not None:
            continue

        cur.execute(
            "INSERT INTO GeniusArtists (genius_artist_id, artist_name, rank) "
            "VALUES (?, ?, ?)",
            (artist_id, artist_name, rank)
        )

        inserted = inserted + 1
        if inserted >= max_new_this_run:
            break

    conn.commit()
    print("Inserted " + str(inserted) + " new Genius artists.")


def main():
    conn, cur = get_connection()
    create_tables(cur)
    store_genius_data(conn, cur)
    conn.close()


if __name__ == "__main__":
    main()
