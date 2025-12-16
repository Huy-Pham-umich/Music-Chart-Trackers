import sqlite3
import matplotlib.pyplot as plt

# Connect to database
conn = sqlite3.connect("music_data.db")
cur = conn.cursor()

# Query with JOIN
cur.execute("""
    SELECT g.genre_name, COUNT(*) as count
    FROM Songs s
    JOIN Genres g ON s.genre_id = g.genre_id
    GROUP BY g.genre_name
""")
results = cur.fetchall()

# Prepare data
genres = [row[0] for row in results]
counts = [row[1] for row in results]

# Bar graph
colors = ['red', 'orange', 'yellow', 'green', 'blue', 'purple', 
          'lightcoral', 'peachpuff', 'wheat', 'lightgreen', 'lightblue', 'plum',
          'darkred', 'darkorange', 'gold', 'darkgreen', 'darkblue', 'indigo', 'grey']
plt.bar(genres, counts, color=colors[:len(genres)])
plt.xlabel("Genre")
plt.ylabel("Number of Songs")
plt.title("Number of Songs per Genre in Billboard Top 100")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()