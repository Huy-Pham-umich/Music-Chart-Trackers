# analyze_data.py
import sqlite3
import matplotlib.pyplot as plt

DB_NAME = "final_project.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    return conn, cur


def get_lastfm_top_artists(cur):
    """
    Get up to 100 artists ordered by rank.
    """
    cur.execute("""
        SELECT artist_name, listeners, playcount, rank
        FROM LastfmTopArtists
        ORDER BY rank ASC
        LIMIT 100
    """)
    rows = cur.fetchall()
    return rows  # list of (artist_name, listeners, playcount, rank)


def get_bucket_label(rank):
    """
    Return a string label for the rank bucket.
    """
    if rank >= 1 and rank <= 10:
        return "1-10"
    elif rank >= 11 and rank <= 25:
        return "11-25"
    elif rank >= 26 and rank <= 50:
        return "26-50"
    else:
        return "51-100"


def compute_avg_plays_per_listener_by_bucket(rows):
    """
    rows: list of (artist_name, listeners, playcount, rank)

    Returns:
      bucket_avgs: dict {bucket_label: average_ratio}
      bucket_counts: dict {bucket_label: number_of_artists}
    """
    sum_ratios = {}
    counts = {}

    for row in rows:
        artist_name = row[0]
        listeners = row[1]
        playcount = row[2]
        rank = row[3]

        # Avoid division by zero
        if listeners == 0:
            continue

        ratio = float(playcount) / float(listeners)
        bucket = get_bucket_label(rank)

        if bucket in sum_ratios:
            sum_ratios[bucket] = sum_ratios[bucket] + ratio
            counts[bucket] = counts[bucket] + 1
        else:
            sum_ratios[bucket] = ratio
            counts[bucket] = 1

    bucket_avgs = {}
    for bucket in sum_ratios:
        total_ratio = sum_ratios[bucket]
        count = counts[bucket]
        if count > 0:
            avg = total_ratio / float(count)
        else:
            avg = 0.0
        bucket_avgs[bucket] = avg

    return bucket_avgs, counts


def write_bucket_results_to_file(bucket_avgs, bucket_counts,
                                 filename="lastfm_bucket_results.txt"):
    """
    Write the average plays per listener by bucket to a text file.
    """
    with open(filename, "w") as f:
        f.write("Last.fm Top 100 Artists — Plays per Listener by Rank Bucket\n\n")
        f.write("Bucket\tArtists\tAvg Plays per Listener\n")

        buckets = list(bucket_avgs.keys())
        buckets.sort()

        for bucket in buckets:
            avg = bucket_avgs[bucket]
            count = bucket_counts[bucket]
            line = (bucket + "\t" +
                    str(count) + "\t" +
                    "{0:.3f}".format(avg) + "\n")
            f.write(line)


def plot_bucket_bar_chart(bucket_avgs):
    """
    Bar chart: x = bucket label, y = average plays per listener.
    """
    buckets = list(bucket_avgs.keys())
    buckets.sort()

    values = []
    for bucket in buckets:
        values.append(bucket_avgs[bucket])

    plt.figure()
    plt.bar(buckets, values)
    plt.title("Last.fm Top 100 Artists:\nAverage Plays per Listener by Rank Bucket")
    plt.xlabel("Rank bucket")
    plt.ylabel("Average plays per listener")
    plt.tight_layout()
    plt.savefig("lastfm_bucket_plays_per_listener.png")
    plt.close()


def main():
    conn, cur = get_connection()

    rows = get_lastfm_top_artists(cur)
    bucket_avgs, bucket_counts = compute_avg_plays_per_listener_by_bucket(rows)

    write_bucket_results_to_file(bucket_avgs, bucket_counts)
    plot_bucket_bar_chart(bucket_avgs)

    conn.close()
    print("Last.fm analysis complete.")


if __name__ == "__main__":
    main()
