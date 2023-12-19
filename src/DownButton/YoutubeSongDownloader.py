from __future__ import unicode_literals
from pathlib import Path
import youtube_dl
import os
import time

DOWNLOAD_DIR = Path("Downloads")
"""
The directory to which the song is downloaded to.
"""

# TODO: show download percentage
# TODO: send a download link to client
# TODO: update metadata
# TODO: make testers
# TODO Queue mechanism
# TODO get song url from name


def get_song_url(song_name: str) -> str:
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


class YoutubeSongDownloader:
    """
    This class represents a download of a song from YouTube
    """

    def __init__(self, song_url, file_type):
        self.song_name = None
        self.song_duration = None
        self.song_url = song_url
        self.file_type = file_type
        self.download_progress = 0
        self.update_song_details()
        file_name = get_valid_file_name(self.song_name)
        self.song_path = Path(os.path.join(DOWNLOAD_DIR, "".join((file_name, ".", file_type))))

    def progress_hook(self, d) -> None:
        """
        Used by youtube_dl while downloading to show progress percentage.
        :param d:
        :return:
        """
        if (d['status'] == 'downloading') and (self.download_progress != "100.0%") \
                and (d['_percent_str'] != self.download_progress):
            self.download_progress = d['_percent_str']
            print(f"Download progress: {self.download_progress}")
            time.sleep(0.2)

    def download_song(self) -> None:
        """
        Downloads the song to the server.
        :return:
        """
        ydl_opts_mp3 = {'format': 'bestaudio/best',
                        'outtmpl': f'{DOWNLOAD_DIR}/%(title)s.%(ext)s',
                        'progress_hooks': [self.progress_hook],
                        'quiet': True,
                        }
        """
                                'postprocessors': [{
                            'key': 'FFmpegVideoConvertor',
                            'preferedformat': 'mp3'
                        }],
        """
        ydl_opts_mp4 = {'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                        'outtmpl': f'{DOWNLOAD_DIR}/%(title)s.%(ext)s',
                        'progress_hooks': [self.progress_hook],
                        'quiet': True
                        }
        if self.file_type == "mp3":
            ydl_opts = ydl_opts_mp3
        elif self.file_type == "mp4":
            ydl_opts = ydl_opts_mp4
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([self.song_url])

    def update_song_details(self) -> None:
        """
        Updates the object representing the song download, such as song duration and name.
        :return:
        """
        with youtube_dl.YoutubeDL({'quiet': True}) as ydl:
            result = ydl.extract_info(self.song_url, download=False)
            self.song_name = result['title']
            self.song_duration = result['duration']

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


def get_download_link(song_path):
    pass

def update_file_metadata():
    pass


def main():
    """
    Used for testing, will be deleted later
    :return:
    """
    url = "https://www.youtube.com/watch?v=bpOSxM0rNPM"  # Do i wanna know
    dl1 = YoutubeSongDownloader(url, "mp3")
    # dl1.download_song()
    dl2 = YoutubeSongDownloader(url, "mp4")
    # dl2.download_song()
    # dl1.download_song_mp3()
    print(dl1.song_path)
    print(dl2.song_path)
    # dl1.get_download_link("mp3")
    # # dl1.get_download_link()
    # app.run(debug=True)


if __name__ == "__main__":
    main()


