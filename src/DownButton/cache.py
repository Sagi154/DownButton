import sqlite3
from datetime import datetime
import logging
from YoutubeSongDownloader import DOWNLOAD_DIR
from pathlib import Path
from pprint import pprint
import os

DB_NAME: str = "Downloads cache.sqlite3"
"""
Name of the database used to keep data of song downloads.
"""
DAYS_OF_CACHE: int = 2
"""
Number of days to save downloaded songs in cache.
"""


# TODO: Make an update by popularity method - optional

def create_testing_cache():
    """

    :return:
    """
    with sqlite3.connect(DB_NAME) as conn:
        command = """
            CREATE TABLE IF NOT EXISTS Playlists (
            playlist_name TEXT PRIMARY KEY,
            date_added datetime,
            download_count INTEGER
            ); """
        conn.execute(command)
        conn.commit()


def set_cache_time(duration: int) -> None:
    """
    Updates the number of days to keep cache.
    for Example: 1 day means only today.
    :param duration: new number of days to keep cache.
    :return:
    """
    global DAYS_OF_CACHE
    DAYS_OF_CACHE = duration
    update_cache_by_date()


def is_song_in_cache(song_name: str, file_type: str) -> bool:
    """
    Checks to see if the song is in the DB.
    :param song_name: The name of the song.
    :param file_type: The type of file of the song.
    :return: True if song is in cache, False otherwise.
    """
    exists = False
    with sqlite3.connect(DB_NAME) as conn:
        command = "SELECT * FROM Songs WHERE song_name = ? AND file_type = ?;"
        cursor = conn.execute(command, (song_name, file_type))
        conn.commit()
        exists = bool(len(cursor.fetchall()))
        if exists:
            logging.info(f"Found song {song_name}.{file_type} in cache.")
        else:
            logging.info(f"Song {song_name}.{file_type} not in cache.")
    return exists


def update_song_count_in_cache(song_name: str, file_type: str) -> None:
    """
    Increments the number of downloads of the song by 1.
    This method is called when the song has already been downloaded and is kept in the cache.
    :param song_name: The name of the song.
    :param file_type: The type of file of the song.
    :return:
    """
    with sqlite3.connect(DB_NAME) as conn:
        command = """
        UPDATE Songs SET download_count = download_count + 1 
        WHERE song_name = ? AND file_type = ? 
        """
        conn.execute(command, (song_name, file_type))
        conn.commit()
        logging.info(f"Incremented song {song_name}.{file_type} download count by 1.")


def add_song_to_cache(song_name: str, file_type: str) -> None:
    """
    This method adds the info of the song into the DB.
    :param song_name: The name of the song.
    :param file_type: The type of file of the song.
    :return:
    """
    with sqlite3.connect(DB_NAME) as conn:
        command = """INSERT OR IGNORE INTO Songs (song_name, file_type, download_count, last_added) 
        VALUES(?, ?, 1, ?);"""
        conn.execute(command, (song_name, file_type, datetime.now().date()))
        conn.commit()
        logging.info(f"Song {song_name}.{file_type} has been added to the cache.")


def get_songs_in_db() -> list:
    """
    This method is used to get all the songs in the DB.
    :return: A list of dicts that each dict represents a song in the DB.
    """
    songs_list = []
    with sqlite3.connect(DB_NAME) as conn:
        command = """
        SELECT * FROM Songs
        """
        cursor = conn.execute(command)
        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        for row in rows:
            songs_list.append(dict(zip(columns, row)))
        conn.commit()
    return songs_list


def get_songs_in_directory() -> list:
    """
    This method is used to get all the songs in the downloads directory.
    :return: A list of dicts that each dict represents a song in the directory.
    """
    songs = [(os.path.splitext(file)[0], os.path.splitext(file)[1][1:]) for file in os.listdir(DOWNLOAD_DIR)
                  if file.endswith("mp3") or file.endswith("mp4")]
    columns = ["song_name", "file_type"]
    songs_list = []
    for song in songs:
        songs_list.append(dict(zip(columns, song)))
    return songs_list


def delete_song_from_directory(song_name: str, file_type: str) -> None:
    """
    Deletes the song from the Downloads directory (DOWNLOAD_DIR).
    :param song_name: The name of the song.
    :param file_type: The type of the file to remove, either MP3 or MP4.
    :return:
    """
    file_name = f"{song_name}.{file_type}"
    file_path = Path(f"{DOWNLOAD_DIR}/{file_name}")
    if file_path.exists():
        file_path.unlink()
        logging.info(f"Song {song_name}.{file_type} has been successfully removed from the directory")
    else:
        print("File not found")


def remove_song_from_cache(song_name: str, file_type: str) -> None:
    """
    Removes the specified song from the Downloads directory and the database.
    :param song_name: The name of the song.
    :param file_type: The type of the file to remove, either MP3 or MP4.
    :return:
    """
    delete_song_from_directory(song_name, file_type)
    with sqlite3.connect(DB_NAME) as conn:
        command = """
            DELETE FROM Songs
            WHERE song_name = ? AND file_type = ?
        """
        conn.execute(command, (song_name, file_type))
        conn.commit()
        logging.info(f"Song {song_name}.{file_type} has been successfully removed from cache")


def update_cache_by_date() -> None:
    """
    This method updates the cache and removes all songs that.
     haven't been downloaded in last DAYS_OF_CACHE days.
    :return:
    """
    today = datetime.now().date()
    songs = get_songs_in_db()
    songs_removed = []
    for song in songs:
        song_date = datetime.fromisoformat(song["last_added"]).date()
        days_in_cache_since_last_download = (today - song_date).days + 1
        if days_in_cache_since_last_download > DAYS_OF_CACHE:
            remove_song_from_cache(song["song_name"], song["file_type"])
            songs_removed.append(f"{song['song_name']}.{song['file_type']}")
    logging.info(f"The following songs have been removed from cache: {songs_removed}")


def get_total_downloads_count() -> int:
    """

    :return: Total count of downloads of songs on the site.
    """
    total_downloads = 0
    with sqlite3.connect(DB_NAME) as conn:
        command = """
        SELECT download_count FROM Songs
        """
        download_counts = conn.execute(command)
        print(download_counts)
        for val in download_counts:
            print(val[0])
            total_downloads += val[0]
    logging.info(f"Total count of downloads is: {total_downloads}")
    return total_downloads


def update_cache_by_popularity() -> None:
    """
    Makes sure unpopular songs are not kept in cache for too long.
    :return:
    """
    pass


def locate_songs_missing_from_directory() -> list:
    """
    Looks for songs that are present in the database but
    are not present in the Downloads directory.
    :return: A list of dicts that each dict represents a song in the database.
    """
    songs_in_db = get_songs_in_db()
    mismatches = []
    for song in songs_in_db:
        song_name = song["song_name"]
        file_type = song["file_type"]
        file_name = f"{song_name}.{file_type}"
        file_path = Path(f"{DOWNLOAD_DIR}/{file_name}")
        if not file_path.exists():
            mismatches.append(song)
    return mismatches


def locate_songs_missing_from_db() -> list:
    """
    Looks for songs that are present in the Downloads directory but
    are not present in the database.
    :return: A list of dicts that each dict represents a song in the Downloads directory.
    """
    songs_in_dir = get_songs_in_directory()
    mismatches = []
    for song in songs_in_dir:
        if not is_song_in_cache(song["song_name"], song["file_type"]):
            mismatches.append(song)
    return mismatches


def remove_mismatches_from_cache() -> None:
    """
    Removes songs that do not appear on both the database and the Downloads directory.
    :return:
    """
    songs_missing_from_db = locate_songs_missing_from_db()
    songs_missing_from_dir = locate_songs_missing_from_directory()
    for song in songs_missing_from_db:
        remove_song_from_cache(song["song_name"], song["file_type"])
    for song in songs_missing_from_dir:
        remove_song_from_cache(song["song_name"], song["file_type"])


def main():
    """
    Used for testing, will be deleted later
    :return:
    """
    song = "Arctic Monkeys - Are You Mine"
    file_type = "mp3"
    song_url = "https://www.youtube.com/watch?v=bpOSxM0rNPM"
    print("Adding song...")
    add_song_to_cache(song, file_type)
    if is_song_in_cache(song, "mp3"):
        print("song added")
    mismatches = locate_songs_missing_from_directory()
    print("Songs missing from directory:")
    for mismatch in mismatches:
        print(mismatch)
    mismatches2 = locate_songs_missing_from_db()
    print("Songs missing from data base:")
    for mismatch in mismatches2:
        print(mismatch)
    print("Removing mismatches from cache")
    remove_mismatches_from_cache()




if __name__ == "__main__":
    main()
