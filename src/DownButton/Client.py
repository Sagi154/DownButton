import random
from time import sleep
from fastapi import FastAPI, WebSocket
import json
from YouTubeMainDownloader import *
from mainApp import is_url, is_youtube_video
from cache import *

MAXIMUM_VIDEO_DURATION_IN_MINUTES = 10
FILE_NAME_RANDOM_STR_LENGTH = 3
CHOICES = "abcdefghijklmnopqrstuvwxyz0123456789"
DOWNLOAD_URL = "http://127.0.0.1:8000/"
LINK_PREFIX = f"{DOWNLOAD_URL}/{DOWNLOAD_DIR}/"

# TODO: make progress classes - ***
# TODO: work out case where user entered not a song name - ***
# TODO: Download playlist functionality - *
# TODO: move mainApp functions here as static methods - ***
# TODO: handle case where 2 clients try to download the same song simultaneously - add random str to file name at else
"""
is_youtube_video fix: 
make it so get_song_url_by_name returns some string that is_youtube_video recognizes and returns False
"""


class Client:
    def __init__(self, websocket: WebSocket, manager: list[WebSocket]):
        self.websocket = websocket
        # should manager and queue be constants?
        self.manager = manager
        # self.queue = queue

    async def start(self):
        data = await self.websocket.receive_text()
        json_data = json.loads(data)
        song_id = json_data["song_id"]
        file_type = json_data["file_type"]
        if not is_url(song_id):
            # Checks if user entered a song name
            song_id = get_song_url_by_name(song_id)
        if not is_youtube_video(song_id):
            #  Checks if URL is valid YouTube video TODO: make sure it works properly
            # maybe change with a class such as ProgressMessage/State
            await self.websocket.send_json({"state": "error_666", "message": "Song not found"})
        else:
            dl = YouTubeMainDownloader(song_id, file_type, self._progress_hook)
            song_duration = dl.get_song_duration()
            if not song_duration < (MAXIMUM_VIDEO_DURATION_IN_MINUTES * 60):
                # Checks if the video is not a song length
                await self.websocket.send_json(
                    {"state": "error_666",
                     "message": "Video duration too long to be a song video"
                     })
            else:
                # Song found, proceed to download
                # make a download queue object and limit number of concurrent downloads
                await self.websocket.send_json({"state": "starting", "song_name": dl.song_name})
                sleep(1.5)
                if is_song_in_cache(dl.youtube_id, dl.song_name, dl.file_type):
                    # Checks if song is saved in cache
                    update_song_count_in_cache(dl.youtube_id, dl.song_name, dl.file_type)
                    await self.song_in_cache_progress()
                else:
                    random_string = ''.join(random.choice(CHOICES) for i in range(FILE_NAME_RANDOM_STR_LENGTH))
                    dl.download_song(random_string)
                    dl.song_name = f"{dl.song_name}_{random_string}"
                    add_song_to_cache(dl.youtube_id, dl.song_name, dl.file_type)
                file_name = get_song_file_name(dl.youtube_id, dl.file_type)
                await self.websocket.send_json({"state": "finished",
                                                "link": f"{LINK_PREFIX}{file_name}"})
                # await self.websocket.send_json({"state": "finished",
                #                                 "link": f"{DOWNLOAD_DIR}/{file_name}"})
                logging.debug(f"link sent {LINK_PREFIX}{file_name}")

    async def _progress_hook(self, percent: float):
        if not percent == 100.0:
            await self.websocket.send_json({
                "state": "downloading",
                "perc": f"{percent}%"
            })
        else:
            await self.websocket.send_json({
                "state": "downloading",
                "perc": "99.9%"
            })

    async def song_in_cache_progress(self):
        perc = 1.0
        while perc <= 100.0:
            await self.websocket.send_json({
                "state": "downloading",
                "perc": f"{perc}%"
            })
            perc += 1.0
            sleep(0.03)
