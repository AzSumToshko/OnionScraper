import logging
from config import LOGGING_FORMAT


class LoggingService:

    @staticmethod
    def initialize_logger(level=logging.INFO):

        logging.basicConfig(
            format=LOGGING_FORMAT,
            level=level
        )

        logging.getLogger("stem").setLevel(logging.WARNING)
        logging.getLogger("stem.control").setLevel(logging.WARNING)

        return logging.getLogger(__name__)