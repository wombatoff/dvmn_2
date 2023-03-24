import json
from datetime import datetime

import requests
import telegram
from environs import Env

env = Env()
env.read_env()

DVMN_TOKEN = env.str("DVMN_TOKEN")
TELEGRAM_TOKEN = env.str("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = env.int("TELEGRAM_CHAT_ID")
DVMN_URL_LONG_POLL = "https://dvmn.org/api/long_polling/"

dvmn_checker_bot = telegram.Bot(token=TELEGRAM_TOKEN)
timestamp = 0

while True:
    try:
        raw_response = requests.get(
            DVMN_URL_LONG_POLL,
            headers={"Authorization": f"Token {DVMN_TOKEN}"},
            params={"timestamp": timestamp},
            timeout=99,
        )
        try:
            json_response = raw_response.json()
        except json.JSONDecodeError:
            print("Ошибка при декодировании JSON ответа.")
            continue

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
                if "timestamp" in attempt:
                    timestamp = attempt["timestamp"]

    except requests.exceptions.ConnectionError:
        print("Ошибка подключения. Проверьте ваше интернет-соединение.")

    except requests.exceptions.Timeout:
        print("Превышено время ожидания. Попробуйте снова.")
