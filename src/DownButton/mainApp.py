from cache import *
from YouTubeMainDownloader import *
from urllib.parse import urlparse
import random

CHOICES = "abcdefghijklmnopqrstuvwxyz0123456789"
MAXIMUM_VIDEO_DURATION_IN_MINUTES = 10

def generate_random_str_for_name(length: int) -> str:
    """
    Generates a random string of length {length} consisting integers and english letters.
    :param length: The length of the random str generator.
    :return: A string of random characters.
    """
    random_string = ''.join(random.choice(CHOICES) for i in range(length))
    return random_string

print(f"random: {generate_random_str_for_name(3)}")
print(CHOICES.lower())



def download_song_button(song_id: str, file_type: str) -> None:
    """
    Method to call when user clicks the download button of a song.
    :param song_id: Name or YouTube URL of the song.
    :param file_type: Either MP3 or MP4.
    :return:
    """
    # if file_type != "mp3" or file_type != "mp4":
    #     return "Invalid file type"
    # Make sure on frond end to receive only mp3 or mp4 as file types
    # Checks if user entered a song name
    if not is_url(song_id):
        song_url = get_song_url_by_name(song_id)
    # User entered a URL
    else:
        song_url = song_id
    return download_song_by_url(song_url, file_type)


def download_song_by_url(song_id: str, file_type: str) -> str:
    """

    :param song_id: Name or YouTube URL of the song.
    :param file_type: Either MP3 or MP4.
    :return: A link to download the song.
    """
    #  Checks if URL is valid YouTube video, possibly do on front end
    if is_youtube_video(song_id):
        dl = YouTubeMainDownloader(song_id, file_type)
        # Checks if the video is a song length, possibly do on front end
        if dl.get_song_duration() < (MAXIMUM_VIDEO_DURATION_IN_MINUTES * 60):
            # Checks if song is saved in cache
            if is_song_in_cache(dl.song_name, file_type):
                update_song_count_in_cache(dl.song_name, file_type)
            else:
                dl.download_song()
                add_song_to_cache(dl.get_song_name(), file_type)
            return get_download_link(dl.song_path)
            # return get_download_link(dl.song_path)
        else:
            return "Video duration too long to be a song video"
    else:
        return "This is not a YouTube video URL"


def download_playlist_button(playlist_url: str):
    """
    Method to call when user clicks the download button of a playlist.
    :param playlist_url: url link to a YouTube playlist.
    :return:
    """
    pass


def is_url(song_id: str) -> bool:
    """
    Checks if a given string is a URL link.
    :param song_id: Name or URL of a possible song.
    :return: True if a URL, False otherwise.
    """
    try:
        result = urlparse(song_id)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def is_youtube_video(song_url: str) -> bool:
    """
    Checks if a given URL is a YouTube link.
    :param song_url: URL of a possible song.
    :return: True if a YouTube URL, False otherwise.
    """
    parsed_url = urlparse(song_url)
    # Check if the domain is YouTube.com or youtu.be
    if parsed_url.netloc == 'www.youtube.com' or parsed_url.netloc == 'youtu.be':
        # Check if the path includes '/watch' for standard YouTube video URLs
        if '/watch' in parsed_url.path:
            return True
        # Check if the path is a short video ID for youtu.be URLs
        elif len(parsed_url.path) > 1:
            return True
    return False


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
