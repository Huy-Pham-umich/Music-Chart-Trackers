import sqlite3

# Connect to your existing database
conn = sqlite3.connect("music_data.db")
cur = conn.cursor()

# JOIN Songs and Genres, count songs per genre
cur.execute("""
    SELECT g.genre_name, COUNT(*) as genre_count
    FROM Songs s
    JOIN Genres g ON s.genre_id = g.genre_id
    GROUP BY g.genre_name
""")

results = cur.fetchall()

# Total number of songs
cur.execute("SELECT COUNT(*) FROM Songs")
total_songs = cur.fetchone()[0]

# Write to TXT file
with open("Spotify_Calculations.txt", "w") as f:
    f.write("Genre Percentages:\n")
    f.write("=================\n")
    for genre_name, count in results:
        percentage = round((count / total_songs) * 100, 2)
        f.write(f"Genre: {genre_name}, Count: {count}, Percentage: {percentage}%\n")

print("Genre percentages written to Spotify_Calculations.txt")

conn.close()