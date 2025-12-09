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

"""result = search_for_artist(token, "acdc")
artist_id = result["id"]
arist_genre = result["genres"]
artist_popularity = result["popularity"]

print(f"Artist Pop: {artist_popularity}")
print(f"Artist Genres: {arist_genre}")

songs = get_songs_by_artist(token, artist_id)
for idx, song in enumerate(songs):
    print(f"{idx + 1}. {song['name']}")"""

"""result = search_for_playlist(token, "Billboard Hot 100")
playlist_id = result["id"]
playlist_name = result["name"]
print(playlist_name)
songs = get_songs_by_playlist(token, playlist_id)

for idx, song in enumerate(songs):
    # Collect artist names
    artist_names = ", ".join([artist["name"] for artist in song["artists"]])
    
    # Get the first artist’s genre
    first_artist_id = song["artists"][0]["id"]
    artist_info = get_artist_info(token, first_artist_id)
    
    popularity = artist_info["popularity"]
    genres = artist_info.get("genres", [])
    genre = genres[0] if genres else "Unknown"

    
    print(f"{idx + 1}. {artist_names} | {song['name']} | Popularity: {popularity} |  Genre: {genre}")"""
    
token = get_token()
result = search_for_playlist(token, "Billboard Hot 100")
playlist_id = result["id"]
playlist_name = result["name"]
print(f"Playlist: {playlist_name}\n")
songs = get_songs_by_playlist(token, playlist_id)

# ------------------ DATABASE SETUP ------------------

conn = sqlite3.connect("billboard.db")
cur = conn.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS Artists (
    artist_id INTEGER PRIMARY KEY,
    artist_name TEXT NOT NULL
)""")

cur.execute("""CREATE TABLE IF NOT EXISTS Genres (
    genre_id INTEGER PRIMARY KEY,
    genre_name TEXT NOT NULL
)""")

cur.execute("""CREATE TABLE IF NOT EXISTS Songs (
    song_name TEXT NOT NULL,
    artist_id INTEGER,
    popularity INTEGER,
    genre_id INTEGER,
    FOREIGN KEY (artist_id) REFERENCES Artists(artist_id),
    FOREIGN KEY (genre_id) REFERENCES Genres(genre_id)
)""")

artist_map = {}
genre_map = {}
artist_counter = 0
genre_counter = 0

# ------------------ DATA INSERTION ------------------

for idx, song in enumerate(songs):
    artist_name = song["artists"][0]["name"]
    # assign artist ID
    if artist_name not in artist_map:
        artist_map[artist_name] = artist_counter
        cur.execute("INSERT INTO Artists VALUES (?, ?)", (artist_counter, artist_name))
        artist_counter += 1
    artist_id = artist_map[artist_name]

    # get genre info
    first_artist_id = song["artists"][0]["id"]
    artist_info = get_artist_info(token, first_artist_id)
    popularity = artist_info["popularity"]
    genres = artist_info.get("genres", [])
    genre_name = genres[0] if genres else "Unknown"

    # assign genre ID
    if genre_name not in genre_map:
        genre_map[genre_name] = genre_counter
        cur.execute("INSERT INTO Genres VALUES (?, ?)", (genre_counter, genre_name))
        genre_counter += 1
    genre_id = genre_map[genre_name]

    # insert song record
    cur.execute("INSERT INTO Songs VALUES (?, ?, ?, ?)",
                (song["name"], artist_id, popularity, genre_id))

    print(f"{idx+1}. {artist_name} | {song['name']} | Popularity: {popularity} | Genre: {genre_name}")

conn.commit()
conn.close()
