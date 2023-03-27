import datetime

import logging
import os

from datetime import datetime
from logging.handlers import TimedRotatingFileHandler


def setup_logging(logs_folder="logs"):
    current_date = datetime.now().strftime("%Y-%m-%d")

    if not os.path.exists(logs_folder):
        os.makedirs(logs_folder)

    log_filename = f"log_file_{current_date}.log"
    log_file = os.path.join(logs_folder, log_filename)
    file_handler = TimedRotatingFileHandler(log_file, when="midnight", interval=1, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

    bot_logger = logging.getLogger(__name__)
    bot_logger.setLevel(logging.DEBUG)
    bot_logger.addHandler(file_handler)

    return bot_logger
