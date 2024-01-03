class StateMessage:
    STATE = None

    def serialize(self):
        json_data = {
            "state": self.STATE,
            **self._serialize()
        }
        return json_data


class ErrorMessage(StateMessage):
    STATE = "error_666"
    ERROR_NOT_FOUND = "Song not found blyat"
    ERROR_SONG_DURATION = "Video duration too long schlong to be a song video"

    def __init__(self, error_type):
        if error_type == "not_found":
            self.error_message = self.ERROR_NOT_FOUND
        elif error_type == "song_duration":
            self.error_message = self.ERROR_SONG_DURATION

    def _serialize(self):
        return {
            "message": self.error_message
        }


class DownloadQueueMessage(StateMessage):
    STATE = "queue"
    QUEUE_MESSAGE = "Currently queueing for download"

    def __init__(self):
        pass

    def _serialize(self):
        return {
            "message": self.QUEUE_MESSAGE
        }


class StartingDownloadMessage(StateMessage):
    STATE = "Starting"

    def __init__(self, song_name):
        self.song_name = song_name

    def _serialize(self):
        return {
            "song_name": self.song_name
        }


class DownloadingMessage(StateMessage):
    STATE = "downloading"

    def __init__(self, percentage):
        self.progress_perc = percentage

    def _serialize(self):
        return {
            "perc": f"{self.progress_perc}%"
        }


class FinishedDownloadMessage(StateMessage):
    STATE = "finished"

    def __init__(self, download_link):
        self.download_link = download_link

    def _serialize(self):
        return {
            "link": self.download_link
        }
