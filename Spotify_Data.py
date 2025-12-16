# Names: Bao Huy Jaden Pham and Felicia Wang
# Student IDs: 34833492 and 62645970
# Emails: huypham@umich.edu and wangfeli@umich.edu

from dotenv import load_dotenv
import os
import base64
from requests import post, get
import json
import sqlite3

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

def get_token():
    # Function to get Spotify API token using client_id and client_secret
    
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")
    
    url = 'https://accounts.spotify.com/api/token'
    
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

def get_auth_header(token):
    # Function to create authorization header for Spotify API requests
    
    return {"Authorization": "Bearer " + token}

#--------------------------------------------------------------------------------------------
# Artist functions

def search_for_artist(token, artist_name):
    # Function to search for an artist by name
    
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    
    #could be type=artist, album, track, playlist, etc.
    query = f"?q={artist_name}&type=artist&limit=1"
    query_url = url + query
    
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)["artists"]["items"]
    
    if len(json_result) == 0:
        print("No artist found with that name...")
        return None
        
    return json_result[0]

def get_songs_by_artist(token, aritst_id):
    # Function to get songs by artist ID
    
    url = f"https://api.spotify.com/v1/artists/{aritst_id}/top-tracks?country=US"
    headers = get_auth_header(token)
    
    result = get(url, headers=headers)
    json_result = json.loads(result.content)["tracks"]
    
    return json_result

def get_artist_info(token, artist_id):
    # Function to get artist details (including genres)
    url = f"https://api.spotify.com/v1/artists/{artist_id}"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    return json.loads(result.content)

#--------------------------------------------------------------------------------------------
# Playlist functions

def search_for_playlist(token, playlist_name):
    # Function to search for a playlist by name
    
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    
    query = f"?q={playlist_name}&type=playlist&limit=1"
    query_url = url + query
    
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)["playlists"]["items"]
    
    if len(json_result) == 0:
        print("No playlist found with that name...")
        return None
        
    return json_result[0]

def get_songs_by_playlist(token, playlist_id):
    # Function to get songs by playlist ID
    
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = get_auth_header(token)
    
    result = get(url, headers=headers)
    json_result = json.loads(result.content)["items"]
    
    songs = []
    for item in json_result:
        songs.append(item["track"])
        
    return songs

#--------------------------------------------------------------------------------------------
# Main code to test the functions
    
token = get_token()
result = search_for_playlist(token, "old songs(2000-2017)")
playlist_id = result["id"]
playlist_name = result["name"]
print(f"Playlist: {playlist_name}\n")
songs = get_songs_by_playlist(token, playlist_id)


# ------------------ DATABASE SETUP -------------------------------------------------------------
conn = sqlite3.connect("music_data.db")
cur = conn.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS Artists (
    artist_id INTEGER PRIMARY KEY,
    artist_name TEXT UNIQUE NOT NULL
)""")

cur.execute("""CREATE TABLE IF NOT EXISTS Genres (
    genre_id INTEGER PRIMARY KEY,
    genre_name TEXT UNIQUE NOT NULL
)""")

cur.execute("""CREATE TABLE IF NOT EXISTS Songs (
    song_name TEXT NOT NULL,
    artist_id INTEGER,
    popularity INTEGER,
    genre_id INTEGER,
    UNIQUE(song_name, artist_id),
    FOREIGN KEY (artist_id) REFERENCES Artists(artist_id),
    FOREIGN KEY (genre_id) REFERENCES Genres(genre_id)
)""")

artist_map = {}
genre_map = {}
artist_counter = 0
genre_counter = 0

# Determine offset based on how many songs already stored
cur.execute("SELECT COUNT(*) FROM Songs")
offset = cur.fetchone()[0]
batch = songs[offset:offset+25]

for idx, song in enumerate(batch, start=offset+1):
    artist_name = song["artists"][0]["name"]

    # Insert artist and get ID
    cur.execute("INSERT OR IGNORE INTO Artists (artist_name) VALUES (?)", (artist_name,))
    cur.execute("SELECT artist_id FROM Artists WHERE artist_name = ?", (artist_name,))
    artist_id = cur.fetchone()[0]

    # Get genre info
    first_artist_id = song["artists"][0]["id"]
    artist_info = get_artist_info(token, first_artist_id)
    popularity = artist_info["popularity"]
    genres = artist_info.get("genres", [])
    genre_name = genres[0] if genres else "Unknown"

    # Insert genre and get ID
    cur.execute("INSERT OR IGNORE INTO Genres (genre_name) VALUES (?)", (genre_name,))
    cur.execute("SELECT genre_id FROM Genres WHERE genre_name = ?", (genre_name,))
    genre_id = cur.fetchone()[0]

    # Insert song record
    cur.execute("INSERT OR IGNORE INTO Songs (song_name, artist_id, popularity, genre_id) VALUES (?, ?, ?, ?)",
                (song["name"], artist_id, popularity, genre_id))

    print(f"{idx}. {artist_name} | {song['name']} | Popularity: {popularity} | Genre: {genre_name}")
    
conn.commit()
conn.close()
