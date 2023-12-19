import sqlite3
from datetime import datetime
import logging
from YoutubeSongDownloader import DOWNLOAD_DIR

DB_NAME: str = "Downloads cache.sqlite3"
"""
Name of the database used to keep data of song downloads.
"""
DAYS_OF_CACHE: int = 2
"""
Number of days to save downloaded songs in cache.
"""


# TODO : Delete from directory method
# TODO: Make a method that checks that all songs in DB are actually in the Downloads folder
# TODO: Make an update by popularity method

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
        conn.execute(command, (song_name, file_type, datetime.now().date))
        conn.commit()
        logging.info(f"Song {song_name}.{file_type} has been added to the cache.")


def get_songs_in_cache() -> list:
    """
    This method is used to get all the songs in the DB.
    :return: A list of dicts that each dict represents a song in the cache.
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


def delete_song_from_directory(song_name: str, file_type: str) -> None:
    """
    Deletes the song from the Downloads directory (DOWNLOAD_DIR).
    :param song_name: The name of the song.
    :param file_type: The type of the file to remove, either MP3 or MP4.
    :return:
    """
    pass


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
    songs = get_songs_in_cache()
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


def main():
    """
    Currently it is used solely for testing.
    :return:
    """
    song = "Arctic Monkeys - Do I Wanna Know (Official Video)"
    remove_song_from_cache(song, "mp3")
    print(is_song_in_cache(song, "mp3"))


if __name__ == "__main__":
    main()
