import asyncio
import logging
import threading
from queue import Queue
import Client
import YouTubeMainDownloader
import time

MAX_CONCURRENT_DOWNLOADS = 1
"""
The limit of concurrent downloads.
"""


class DownloadsManager:
    def __init__(self):
        self.current_downloads_count: int = 0
        """
        The count of the current downloads happening.
        """
        self.download_queue: Queue[(Client, YouTubeMainDownloader)] = asyncio.Queue()
        """
        A queue containing clients who want to download and their downloader.
        """
        self.lock = threading.Lock()

    async def advance_queue(self):
        """
        This method is meant to run continuously while the server is running.
        It awaits till self.download_queue has an object in it.
        Then it waits till that client is cleared to download and calls for download method.
        :return:
        """
        download_request_waiting = False
        download_request = None
        while True:
            if not download_request_waiting:
                download_request = await self.download_queue.get()
                download_request_waiting = True
            if not self.clear_to_download():
                await asyncio.sleep(1)
                continue
            if download_request is None:
                # No more downloads in queue
                break
            client, downloader = download_request
            asyncio.ensure_future(client.cleared_to_download_song(dl=downloader))
            download_request_waiting = False
            download_request = None
            with self.lock:
                self.current_downloads_count += 1

    def clear_to_download(self) -> bool:
        """

        :return: True if client may download, False otherwise.
        """
        if self.current_downloads_count < MAX_CONCURRENT_DOWNLOADS:
            return True
        else:
            return False

    async def add_to_queue(self, client: Client, downloader: YouTubeMainDownloader):
        """

        :param client:
        :param downloader:
        :return:
        """
        download_request = client, downloader
        await client.websocket.send_json({"state": "queue",
                                          "message": "Currently queueing for download"})
        logging.info(f"Client {client.websocket.client} With download {downloader.song_name} has entered queue")
        await self.download_queue.put(download_request)
