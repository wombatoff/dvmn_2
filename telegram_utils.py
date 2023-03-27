import sys

import telegram
from environs import Env

env = Env()
env.read_env()

TELEGRAM_TOKEN = env.str("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = env.int("TELEGRAM_CHAT_ID")


def send_telegram_message(message, bot_logger):
    dvmn_checker_bot = telegram.Bot(token=TELEGRAM_TOKEN)
    try:
        dvmn_checker_bot.send_message(text=message, chat_id=TELEGRAM_CHAT_ID)
        bot_logger.info("Сообщение отправлено.")
    except telegram.error.Unauthorized:
        bot_logger.error("Ошибка авторизации. Проверьте правильность токена и chat_id.")
        sys.exit(1)
    except Exception as e:
        bot_logger.error(f"Не удалось отправить сообщение. Ошибка: {e}")
        sys.exit(1)
