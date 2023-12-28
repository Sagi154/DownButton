from fastapi import WebSocket
from queue import Queue


class DownloadsQueue:
    def __init__(self):
        self.limit = 5
        """
        The limit of concurrent downloads.
        """
        self.current_downloads: list[WebSocket] = []
        self.queue: Queue = []

    def allow_download(self):
        if len(self.current_downloads) < self.limit:
            return True
        else:
            return False

    def add_to_downloads(self, websocket: WebSocket):
        self.current_downloads.append(websocket)

    def download_finished(self, websocket):
        self.current_downloads.remove(websocket)

    def add_to_queue(self, websocket):
        self.queue.put(websocket)

