# Reper Site

Минимальный веб-сайт репетитора для дипломного проекта с интеграцией заявок:

- страницы: главная, запись, контакты;
- форма записи сохраняется в SQLite;
- при настройке переменных окружения заявка отправляется в Telegram.

## Запуск

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app/app.py
```

Откройте `http://127.0.0.1:5000`.

## Переменные окружения

- `FLASK_SECRET_KEY` — секрет Flask;
- `TELEGRAM_BOT_TOKEN` — токен Telegram-бота;
- `TELEGRAM_CHAT_ID` — ID чата для заявок.
