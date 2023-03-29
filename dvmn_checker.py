import logging
import os
import textwrap
import time
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

import requests
from environs import Env

from telegram_utils import send_telegram_message

DVMN_URL_LONG_POLL = "https://dvmn.org/api/long_polling/"


def main(dvmn_token, telegram_token, telegram_chat_id):
    timestamp = 0
    wait_time = 5 * 60

    while True:
        try:
            raw_response = requests.get(
                DVMN_URL_LONG_POLL,
                headers={"Authorization": f"Token {dvmn_token}"},
                params={"timestamp": timestamp},
                timeout=99,
            )
            raw_response.raise_for_status()
            response = raw_response.json()
            if 'error' in response:
                raise requests.exceptions.HTTPError
            bot_logger.debug(response)

            if "new_attempts" in response:
                """ 
                Перебираем все попытки в обратном порядке и отправляем сообщения в телеграм. 
                Берем timestamp последней попытки и передаем его в следующий запрос.                
                """
                for attempt in reversed(response["new_attempts"]):
                    submitted_at = datetime.fromtimestamp(attempt["timestamp"])
                    submitted_at = submitted_at.strftime("%d.%m.%Y %H:%M")
                    if attempt["is_negative"]:
                        message = textwrap.dedent(f"""
                            Работа \"{attempt['lesson_title']}\" 
                            проверена {submitted_at}, в работе есть ошибки.                        
                            {attempt['lesson_url']}
                        """)
                        send_telegram_message(message, bot_logger, telegram_token, telegram_chat_id)
                    else:
                        message = textwrap.dedent(f"""
                            Работа \"{attempt['lesson_title']}\" 
                            проверена {submitted_at}, все бенч.
                            {attempt['lesson_url']}
                        """)
                        send_telegram_message(message, bot_logger, telegram_token, telegram_chat_id)
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
    env = Env()
    env.read_env()

    DVMN_TOKEN = env.str("DVMN_TOKEN")
    TELEGRAM_TOKEN = env.str("TELEGRAM_TOKEN")
    TELEGRAM_CHAT_ID = env.int("TELEGRAM_CHAT_ID")

    if not os.path.exists("logs"):
        os.makedirs("logs")
    log_file = os.path.join("logs", "log_file.log")
    file_handler = TimedRotatingFileHandler(log_file, when="midnight", interval=1, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

    bot_logger = logging.getLogger(__file__)
    bot_logger.setLevel(logging.DEBUG)
    bot_logger.addHandler(file_handler)

    main(DVMN_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)
