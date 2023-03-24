
# Отправляем уведомления о проверке работ
### Описание
Telegram бот, который отправляет уведомления о проверке работ на сайте [dvmn.org](https://dvmn.org/)

### Стек технологий:
- Python
- python-telegram-bot
---


## Запуск проекта локально
Клонировать репозиторий и перейти в него:
```
git clone https://github.com/wombatoff/dvmn_2
cd dvmn_2
```

Создать и активировать виртуальное окружение, обновить pip и установить зависимости:
```
python -m venv venv
source venv/Scripts/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Создать файл .env и заполнить его:
```
DVMN_TOKEN=
TELEGRAM_TOKEN=
TELEGRAM_CHAT_ID=
```

Запустить бота:
```
python dvmn_checker.py
```

### Автор:

[Wombatoff](https://github.com/wombatoff/)