from cache import *
from YouTubeMainDownloader import *
from urllib.parse import urlparse
import random

MAXIMUM_VIDEO_DURATION_IN_MINUTES = 10


def main():
    """
    Used for testing, will be deleted later
    :return:
    """
    # clear_cache()
    # song_link = "https://www.youtube.com/watch?v=bpOSxM0rNPM"  # Do i wanna know
    # song_type = "mp3"
    # song_down = YouTubeMainDownloader(song_link, song_type)
    # song_name = song_down.get_song_name()
    # song_down.download_song()
    # add_song_to_cache(song_name, song_type)
    # print("song downloaded")
    # file_name = f"{get_valid_file_name(song_name)}.{song_type}"
    # file_path = Path(f"{DOWNLOAD_DIR}/{file_name}")
    # print(f"file name: {file_name}")
    # print(f"file path: {file_path}")
    # print(f"locate file: {file_path.exists()}")
    # print(f"in cache: {is_song_in_cache(song_name, song_type)}")

    song_url = "https://www.youtube.com/watch?v=qDXBpUtiX1E"
    file_type = "mp3"
    song_down = YouTubeMainDownloader(song_url, file_type, main)
    print("after dl")
    print(f"song name: {song_down.song_name} and duration: {song_down.song_duration}")
    with youtube_dl.YoutubeDL({'quiet': False}) as ydl:
        result = ydl.extract_info(song_url, download=False)
        song_name = get_valid_file_name(result['title'])
        song_duration = result['duration']
        print(f"song name: {song_name} and duration: {song_duration}")


# if __name__ == "__main__":
#     main()
