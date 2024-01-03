from __future__ import unicode_literals
import asyncio
import logging
import threading
import youtube_dl

DOWNLOAD_DIR = "Downloads"
"""
The directory to which the song is downloaded to.
"""

# TODO: send a download link to client - Sagi
# TODO: update metadata - **
# TODO: make testers - *
# TODO: get song url from name - **
# TODO: Download playlist - *


def get_song_url_by_name(song_name: str) -> str:
    """
    This method gets a song name and returns a link of the song from YouTube.
    :param song_name: The name of the song.
    :return: A YouTube URL of the song.
    """
    pass


def get_valid_file_name(song_name: str) -> str:
    """
    This method is used to get the name of the download file related to the song,
    according to Windows file naming rules.
    :param song_name: The titles of the song in YouTube.
    :return: Returns the name of the song as saved in the Downloads directory.
    """
    illegal_chars = ("/", "\\", "?", ":", "*", "<", ">", "\"", "|")
    return "".join(x for x in song_name if x not in illegal_chars)


class YouTubeMainDownloader:
    """
    This class represents a download of a song from YouTube
    """

    def __init__(self, song_url, file_type, progress_callback):
        self.youtube_id = None
        self.song_name = None
        self.song_duration = None
        self.song_url = song_url
        self.file_type = file_type
        self.download_progress = 0
        self.update_song_download_details()
        # self.file_name = None
        # self.song_path = Path(f"{DOWNLOAD_DIR}/{self.file_name}")
        self.progress_callback = progress_callback

    def progress_hook(self, d) -> None:
        """
        Used by youtube_dl while downloading to show progress percentage.
        :param d: current download.
        :return:
        """
        if d['status'] == "downloading":
            perc = d['_percent_str'].strip()
            self.download_progress = float(perc.rstrip('%'))
            th = threading.Thread(target=self.send_progress_to_websocket, args=(self.download_progress,))
            th.start()
            th.join()

    def send_progress_to_websocket(self, perc: float):
        """
        Used while downloading to send the progression percentage to the websocket.
        :param perc: The current download progression percentage.
        :return:
        """
        asyncio.run(self.progress_callback(perc))

    def download_song(self, random_string: str) -> str:
        """
        Downloads the song to the server.
        :param random_string: A random string that is appended to the name of the downloaded file.
        :return: The name of the downloaded file.
        """
        logging.debug(f"Starting to download {self.song_name}")
        ydl_opts_mp3 = {'format': 'bestaudio/best',
                        'outtmpl': f'{DOWNLOAD_DIR}/%(title)s_{random_string}.%(ext)s',
                        'progress_hooks': [self.progress_hook],
                        'quiet': True,
                        'postprocessors': [{
                            'key': 'FFmpegVideoConvertor',
                            'preferedformat': 'mp3'
                        }, {'key': 'FFmpegMetadata'}],
                        'min_wait': 0.25
                        }
        ydl_opts_mp4 = {'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                        'outtmpl': f'{DOWNLOAD_DIR}/%(title)s_{random_string}.%(ext)s',
                        'progress_hooks': [self.progress_hook],
                        'postprocessors': [{
                            'key': 'FFmpegMetadata'
                        }],
                        'quiet': True,
                        'min_wait': 0.25
                        }
        if self.file_type == "mp3":
            ydl_opts = ydl_opts_mp3
        elif self.file_type == "mp4":
            ydl_opts = ydl_opts_mp4
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([self.song_url])

    def update_song_download_details(self) -> None:
        """
        Updates the object representing the song download, such as song duration and name.
        :return:
        """
        with youtube_dl.YoutubeDL({'quiet': True}) as ydl:
            result = ydl.extract_info(self.song_url, download=False)
            self.song_name = get_valid_file_name(result['title'])
            self.song_duration = result['duration']
            self.youtube_id = result['id']

    def get_song_name(self) -> str:
        """
        Returns the title of the YouTube video.
        :return:
        """
        return self.song_name

    def get_song_duration(self) -> int:
        """
        Returns the duration of the YouTube video in seconds.
        :return:
        """
        return self.song_duration


def main():
    """
    Used for testing, will be deleted later
    :return:
    """

    # song_url = "https://www.youtube.com/watch?v=bpOSxM0rNPM"  # Do i wanna know
    # song_type = "mp3"
    # song_down = YoutubeSongDownloader(song_url, song_type)
    # song_name = song_down.get_song_name()
    # song_down.download_song()
    # print("song downloaded")
    # file_name = f"{get_valid_file_name(song_name)}.{song_type}"
    # file_path = Path(f"{DOWNLOAD_DIR}/{file_name}")
    # print(f"file name: {file_name}")
    # print(f"file path: {file_path}")
    # print(file_path.exists())

    # song_test = "https://www.youtube.com/watch?v=fRk6K-H1Lxc" # kid cudi cudderisback
    # type = "mp3"
    # test_down = YouTubeMainDownloader(song_test, type)
    # print(f"Downloading {test_down.get_song_name()}")
    # test_down.download_song()
    # print("Download complete")
    # file_name = f"{get_valid_file_name(test_down.get_song_name())}.{type}"
    # file_path = Path(f"{DOWNLOAD_DIR}/{file_name}")
    # print(f"file name: {file_name}")
    # print(f"file path: {file_path}")
    # print(file_path.exists())

    # song1 = YouTubeMainDownloader("https://www.youtube.com/watch?v=fRk6K-H1Lxc", "mp3", main )
    # song2 = YouTubeMainDownloader("https://www.youtube.com/watch?v=78DVtcsT26k", "mp3", main)
    # print(f"song1: name={song1.song_name}, id={song1.youtube_id}")
    # print(f"song2: name={song2.song_name}, id={song2.youtube_id}")
    # song1.download_song("bh3")


if __name__ == "__main__":
    main()


