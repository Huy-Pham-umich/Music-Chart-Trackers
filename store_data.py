import sqlite3
import requests

DB_NAME = "lastfm_data.db"

LASTFM_API_KEY = "147d088f8a1a28a41085abb802b8d9dc"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    return conn, cur


def create_tables(cur):
    """
    Create the LastfmTopArtists table.
    artist_id is an integer key.
    artist_name is UNIQUE so we never store the same string twice.
    """
    cur.execute("""
        CREATE TABLE IF NOT EXISTS LastfmTopArtists (
            artist_id INTEGER PRIMARY KEY AUTOINCREMENT,
            artist_name TEXT UNIQUE,
            listeners INTEGER,
            playcount INTEGER,
            rank INTEGER
        )
    """)


def fetch_lastfm_top_artists():
    """
    Call Last.fm chart.getTopArtists and get up to 100 artists.
    We rely on the list order for rank (index + 1).
    """

    base_url = "https://ws.audioscrobbler.com/2.0/"
    url = (base_url +
           "?method=chart.gettopartists" +
           "&api_key=" + LASTFM_API_KEY +
           "&limit=100" +
           "&format=json")

    response = requests.get(url)
    data = response.json()

    artists_block = data["artists"]
    artist_list = artists_block["artist"]

    results = []

    # Walk through the list; index gives us rank.
    for i in range(len(artist_list)):
        artist = artist_list[i]

        name = artist["name"]
        listeners_str = artist["listeners"]
        playcount_str = artist["playcount"]

        # Rank is list position (1-based)
        rank_value = i + 1

        artist_dict = {}
        artist_dict["artist_name"] = name
        artist_dict["listeners"] = int(listeners_str)
        artist_dict["playcount"] = int(playcount_str)
        artist_dict["rank"] = rank_value

        results.append(artist_dict)

    return results


def store_lastfm_data(conn, cur):
    """
    Insert up to 25 new artists per run.
    Avoid duplicates by checking artist_name (UNIQUE).
    Stop once we reach 100 rows total.
    """

    # Count existing rows
    cur.execute("SELECT COUNT(*) FROM LastfmTopArtists")
    row = cur.fetchone()
    current_count = row[0]

    if current_count >= 100:
        print("Already have 100 Last.fm artists. Skipping insert.")
        return

    max_new_this_run = 100 - current_count
    if max_new_this_run > 25:
        max_new_this_run = 25

    artists = fetch_lastfm_top_artists()
    inserted = 0

    for artist in artists:
        name = artist["artist_name"]
        listeners = artist["listeners"]
        playcount = artist["playcount"]
        rank = artist["rank"]

        # Check if this artist_name is already stored
        cur.execute(
            "SELECT 1 FROM LastfmTopArtists WHERE artist_name = ?",
            (name,)
        )
        exists = cur.fetchone()
        if exists is not None:
            continue

        cur.execute(
            "INSERT INTO LastfmTopArtists (artist_name, listeners, playcount, rank) "
            "VALUES (?, ?, ?, ?)",
            (name, listeners, playcount, rank)
        )

        inserted = inserted + 1
        if inserted >= max_new_this_run:
            break

    conn.commit()
    print("Inserted " + str(inserted) + " new Last.fm artists.")


def main():
    conn, cur = get_connection()
    create_tables(cur)
    store_lastfm_data(conn, cur)
    conn.close()


if __name__ == "__main__":
    main()
