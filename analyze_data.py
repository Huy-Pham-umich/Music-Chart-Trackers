import sqlite3
import matplotlib.pyplot as plt

DB_NAME = "final_project.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    return conn, cur


def get_top_100_genius_artists(cur):
    """
    Get up to 100 artists ordered by rank.
    """
    cur.execute("""
        SELECT artist_name, rank
        FROM GeniusArtists
        ORDER BY rank ASC
        LIMIT 100
    """)
    rows = cur.fetchall()
    return rows  # list of (artist_name, rank)


def compute_first_letter_distribution(rows):
    """
    rows: list of (artist_name, rank)
    returns: (counts_dict, total_count)
      counts_dict: {letter: count}
      total_count: total number of artists counted
    """
    counts = {}
    total = 0

    for row in rows:
        artist_name = row[0]

        if artist_name is None:
            continue

        name_stripped = artist_name.strip()
        if len(name_stripped) == 0:
            continue

        first_char = name_stripped[0].upper()

        # Only count A-Z
        if first_char < "A" or first_char > "Z":
            continue

        if first_char in counts:
            counts[first_char] = counts[first_char] + 1
        else:
            counts[first_char] = 1

        total = total + 1

    return counts, total


def write_first_letter_results_to_file(counts, total,
                                       filename="genius_first_letter_results.txt"):
    """
    Write the first-letter frequency distribution to a text file.
    """
    with open(filename, "w") as f:
        f.write("Genius Top Artists — First Letter Frequency Distribution\n\n")
        f.write("Total artists counted: " + str(total) + "\n\n")
        f.write("Letter\tCount\tPercentage\n")

        letters = list(counts.keys())
        letters.sort()

        for letter in letters:
            count = counts[letter]
            if total > 0:
                pct = float(count) / float(total)
            else:
                pct = 0.0
            line = (letter + "\t" +
                    str(count) + "\t" +
                    "{0:.3f}".format(pct) + "\n")
            f.write(line)


def plot_first_letter_bar_chart(counts):
    """
    Bar chart: x = first letter, y = count.
    """
    letters = list(counts.keys())
    letters.sort()
    values = []
    for letter in letters:
        values.append(counts[letter])

    plt.figure()
    plt.bar(letters, values)
    plt.title("Genius Top 100 Artists: First-Letter Frequency")
    plt.xlabel("First letter of artist name")
    plt.ylabel("Number of artists")
    plt.tight_layout()
    plt.savefig("genius_first_letter_distribution.png")
    plt.close()


def main():
    conn, cur = get_connection()

    rows = get_top_100_genius_artists(cur)
    counts, total = compute_first_letter_distribution(rows)

    write_first_letter_results_to_file(counts, total)
    plot_first_letter_bar_chart(counts)

    conn.close()
    print("Genius first-letter analysis complete.")


if __name__ == "__main__":
    main()
