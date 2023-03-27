import datetime
import time
from datetime import datetime

import requests
import telegram
from environs import Env

from log_config import setup_logging

env = Env()
env.read_env()

DVMN_TOKEN = env.str("DVMN_TOKEN")
TELEGRAM_TOKEN = env.str("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = env.int("TELEGRAM_CHAT_ID")
DVMN_URL_LONG_POLL = "https://dvmn.org/api/long_polling/"

bot_logger = setup_logging()


def main():
    dvmn_checker_bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = 0
    connection_retries = 0
    initial_wait_time = 1

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
            connection_retries = 0

            if "new_attempts" in json_response:
                for attempt in reversed(json_response["new_attempts"]):
                    submitted_at = datetime.fromtimestamp(attempt["timestamp"])
                    submitted_at = submitted_at.strftime("%d.%m.%Y %H:%M")
                    if attempt["is_negative"]:
                        message = (
                            f"Работа \"{attempt['lesson_title']}\" проверена {submitted_at}, "
                            f"в работе есть ошибки.\n"
                            f"{attempt['lesson_url']}"
                        )
                        dvmn_checker_bot.send_message(
                            text=message,
                            chat_id=TELEGRAM_CHAT_ID
                        )
                        bot_logger.info(message)
                    else:
                        message = (
                            f"Работа \"{attempt['lesson_title']}\" проверена {submitted_at}, "
                            f"все бенч.\n"
                            f"{attempt['lesson_url']}"
                        )
                        dvmn_checker_bot.send_message(
                            text=message,
                            chat_id=TELEGRAM_CHAT_ID
                        )
                        bot_logger.info(message)
                    if "timestamp" in attempt:
                        timestamp = attempt["timestamp"]

        except requests.exceptions.HTTPError:
            bot_logger.warning("Ошибка HTTP запроса. Проверьте правильность токена.")

        except requests.exceptions.ConnectionError:
            bot_logger.warning("Ошибка подключения. Проверьте ваше интернет-соединение.")

        except requests.exceptions.Timeout:
            bot_logger.warning("Превышено время ожидания. Попробуйте снова.")


if __name__ == "__main__":
    main()
