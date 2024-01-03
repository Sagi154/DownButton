import random
import json
from time import sleep
from urllib.parse import urlparse
from fastapi import WebSocket
from YouTubeMainDownloader import *
from cache import *
from DownloadsManager import DownloadsManager
from ClientInteractions import *

MAXIMUM_VIDEO_DURATION_IN_MINUTES = 10
FILE_NAME_RANDOM_STR_LENGTH = 3
CHOICES = "abcdefghijklmnopqrstuvwxyz0123456789"
DOWNLOAD_URL = "http://127.0.0.1:8000/"
LINK_PREFIX = f"{DOWNLOAD_URL}/{DOWNLOAD_DIR}/"

# TODO: work out case where user entered not a song name - ***
# TODO: Download playlist functionality - *
"""
is_youtube_video fix: 
make it so get_song_url_by_name returns some string that is_youtube_video recognizes and returns False
"""


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


class Client:
    def __init__(self, websocket: WebSocket, conn_manager: list[WebSocket], down_manager: DownloadsManager):
        self.websocket = websocket
        self.conn_manager = conn_manager
        self.down_manager = down_manager
        self.lock = threading.Lock()

    async def start(self) -> None:
        """
        New client requesting a download initiated.
        :return:
        """
        data = await self.websocket.receive_text()
        json_data = json.loads(data)
        if json_data["download_type"] == "song":
            await self.song_download_protocol(json_data)
        elif json_data["download_type"] == "playlist":
            await self.playlist_download_protocol()

    async def song_download_protocol(self, json_data: str) -> None:
        """
        The protocol for when client chooses to download a song.
        :param json_data: JSON form of song_id and file_type the client entered.
        :return:
        """
        song_id = json_data["song_id"]
        file_type = json_data["file_type"]
        if not is_url(song_id):
            # Checks if user entered a song name
            song_id = get_song_url_by_name(song_id)
            # TODO: Make a method that suggests several options for song url from youtube
        if not is_youtube_video(song_id):
            #  Checks if URL is valid YouTube video
            await self.websocket.send_json(ErrorMessage("not_found").serialize())
            return
        dl = YouTubeMainDownloader(song_id, file_type, self._progress_hook)
        song_duration = dl.get_song_duration()
        if not song_duration < (MAXIMUM_VIDEO_DURATION_IN_MINUTES * 60):
            # Checks if the video is not a song length
            await self.websocket.send_json(ErrorMessage("song_duration").serialize())
            return
        # Song found, proceed to download
        with self.lock:
            logging.debug(f"download count is {self.down_manager.current_downloads_count}")
            if self.down_manager.clear_to_download():
                # Download count is under the limit, may proceed to download.
                self.down_manager.current_downloads_count += 1
                asyncio.ensure_future(self.cleared_to_download_song(dl))
            else:
                # Download count limit reached, entered queue.
                await self.websocket.send_json(DownloadQueueMessage().serialize())
                asyncio.ensure_future(self.down_manager.add_to_queue(self, dl))

    async def cleared_to_download_song(self, dl: YouTubeMainDownloader) -> None:
        """
        Once client is cleared to download through the DownloadsManager this method initiates downloading process.
        :param dl: The song downloader object using youtube_dl.
        :return:
        """
        logging.debug(f"Started downloading {dl.song_name},"
                      f" increasing downloads count to {self.down_manager.current_downloads_count}")
        # await self.websocket.send_json({"state": "Starting", "song_name": dl.song_name})
        await self.websocket.send_json(StartingDownloadMessage(dl.song_name).serialize())
        await asyncio.sleep(1.5)
        # Starting download
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.download_song, dl)
        file_name = get_song_file_name(dl.youtube_id, dl.file_type)
        # Retrieve file name for the client link.
        await self.websocket.send_json(FinishedDownloadMessage(f"{LINK_PREFIX}{file_name}").serialize())
        # await self.websocket.send_json({"state": "finished",
        #                                 "link": f"{DOWNLOAD_DIR}/{file_name}"})
        logging.debug(f"link sent {LINK_PREFIX}{file_name}")

    def download_song(self, dl: YouTubeMainDownloader) -> None:
        """
        This method is used to determine whether the song is in the cache or to download using youtube_dl.
        :param dl: The song downloader object using youtube_dl.
        :return:
        """
        flag = is_song_in_cache(dl.youtube_id, dl.song_name, dl.file_type)
        # Checks if song is saved in cache
        if flag:
            update_song_count_in_cache(dl.youtube_id, dl.song_name, dl.file_type)
            asyncio.run(self.song_in_cache_progress())
        else:
            random_string = ''.join(random.choice(CHOICES) for i in range(FILE_NAME_RANDOM_STR_LENGTH))
            dl.download_song(random_string)
            dl.song_name = f"{dl.song_name}_{random_string}"
            add_song_to_cache(dl.youtube_id, dl.song_name, dl.file_type)
        with self.lock:
            self.down_manager.current_downloads_count -= 1
        logging.debug(f"Finished downloading {dl.song_name},"
                      f" decreasing downloads count to {self.down_manager.current_downloads_count}")

    async def playlist_download_protocol(self, data: str):
        pass

    async def _progress_hook(self, percent: float) -> None:
        """

        :param percent: The current download progression percentage.
        :return:
        """
        if not percent == 100.0:
            await self.websocket.send_json(DownloadingMessage(percent).serialize())
        else:
            await self.websocket.send_json(DownloadingMessage(99.9).serialize())

    async def song_in_cache_progress(self) -> None:
        """
        A generated percentage progress for aesthetic purposes.
        :return:
        """
        perc = 1.0
        while perc <= 100.0:
            await self.websocket.send_json(DownloadingMessage(perc).serialize())
            perc += 1.0
            sleep(0.03)
