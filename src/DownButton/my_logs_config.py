import logging


class IgnoreSelectorLogFilter(logging.Filter):
    def filter(self, record):
        """
        Ignore log messages containing "Using selector: SelectSelector" that are coming from the youtube_dl library.
        :param record:
        :return:
        """
        return "Using selector: SelectSelector" not in record.getMessage()


def set_log_config():
    logging.basicConfig(format="[%(levelname)s] %(asctime)s %(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S",
                        encoding='utf-8',
                        handlers=[logging.FileHandler("my_logs.log"),
                                  logging.StreamHandler()],
                        level=logging.DEBUG)
    asyncio_logger = logging.getLogger("asyncio")
    asyncio_logger.addFilter(IgnoreSelectorLogFilter())
