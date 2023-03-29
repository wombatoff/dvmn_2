import sys

import telegram


def send_telegram_message(message, bot_logger, telegram_token, telegram_chat_id):
    dvmn_checker_bot = telegram.Bot(token=telegram_token)
    try:
        dvmn_checker_bot.send_message(text=message, chat_id=telegram_chat_id)
        bot_logger.info("Сообщение отправлено.")
    except telegram.error.Unauthorized:
        bot_logger.error("Ошибка авторизации. Проверьте правильность токена и chat_id.")
        sys.exit(1)
    except Exception as e:
        bot_logger.error(f"Не удалось отправить сообщение. Ошибка: {e}")
        sys.exit(1)
