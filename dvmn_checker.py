import datetime
import time

import requests
from environs import Env

from log_config import setup_logging
from telegram_utils import send_telegram_message

env = Env()
env.read_env()

DVMN_TOKEN = env.str("DVMN_TOKEN")
DVMN_URL_LONG_POLL = "https://dvmn.org/api/long_polling/"

bot_logger = setup_logging()


def main():
    timestamp = 0
    wait_time = 5 * 60

    while True:
        try:
            raw_response = requests.get(
                DVMN_URL_LONG_POLL,
                headers={"Authorization": f"Token {DVMN_TOKEN}"},
                params={"timestamp": timestamp},
                timeout=99,
            )
            raw_response.raise_for_status()
            json_response = raw_response.json()
            if 'error' in json_response:
                raise requests.exceptions.HTTPError

            if "new_attempts" in json_response:
                for attempt in reversed(json_response["new_attempts"]):
                    submitted_at = datetime.datetime.fromtimestamp(attempt["timestamp"])
                    submitted_at = submitted_at.strftime("%d.%m.%Y %H:%M")
                    if attempt["is_negative"]:
                        message = (
                            f"Работа \"{attempt['lesson_title']}\" проверена {submitted_at}, "
                            f"в работе есть ошибки.\n"
                            f"{attempt['lesson_url']}"
                        )
                        send_telegram_message(message, bot_logger)
                    else:
                        message = (
                            f"Работа \"{attempt['lesson_title']}\" проверена {submitted_at}, "
                            f"все бенч.\n"
                            f"{attempt['lesson_url']}"
                        )
                        send_telegram_message(message, bot_logger)
                    if "timestamp" in attempt:
                        timestamp = attempt["timestamp"]

        except (requests.exceptions.HTTPError,
                requests.exceptions.ConnectionError,
                requests.exceptions.Timeout) as e:
            if isinstance(e, requests.exceptions.HTTPError):
                bot_logger.error("Ошибка HTTP запроса.")
            elif isinstance(e, requests.exceptions.ConnectionError):
                bot_logger.error("Ошибка подключения к серверу.")
            else:
                bot_logger.error("Превышено время ожидания.")
            bot_logger.info(f"Ожидание {wait_time} секунд перед следующей попыткой.")
            time.sleep(wait_time)


if __name__ == "__main__":
    main()
