from __future__ import annotations

import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from flask import Flask, flash, redirect, render_template, request, url_for

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "requests.db"


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "dev-secret-change-me")
    app.config["TELEGRAM_BOT_TOKEN"] = os.getenv("TELEGRAM_BOT_TOKEN", "")
    app.config["TELEGRAM_CHAT_ID"] = os.getenv("TELEGRAM_CHAT_ID", "")

    init_db()

    @app.route("/")
    def index() -> str:
        return render_template("index.html")

    @app.route("/booking", methods=["GET", "POST"])
    def booking() -> str:
        if request.method == "POST":
            form = {
                "name": request.form.get("name", "").strip(),
                "contact": request.form.get("contact", "").strip(),
                "subject": request.form.get("subject", "").strip(),
                "lesson_time": request.form.get("lesson_time", "").strip(),
                "comment": request.form.get("comment", "").strip(),
            }

            missing = [key for key, value in form.items() if key != "comment" and not value]
            if missing:
                flash("Заполните обязательные поля формы.", "error")
                return render_template("booking.html", form=form)

            save_request(form)
            sent = send_to_telegram(form, app.config["TELEGRAM_BOT_TOKEN"], app.config["TELEGRAM_CHAT_ID"])
            if sent:
                flash("Заявка отправлена. Мы свяжемся с вами в ближайшее время.", "success")
            else:
                flash("Заявка сохранена. Telegram не настроен или временно недоступен.", "warning")
            return redirect(url_for("booking"))

        return render_template("booking.html", form={})

    @app.route("/contacts")
    def contacts() -> str:
        return render_template("contacts.html")

    return app


def init_db() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS lesson_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                name TEXT NOT NULL,
                contact TEXT NOT NULL,
                subject TEXT NOT NULL,
                lesson_time TEXT NOT NULL,
                comment TEXT
            )
            """
        )


def save_request(form: dict[str, str]) -> None:
    created_at = datetime.now(timezone.utc).isoformat()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT INTO lesson_requests (created_at, name, contact, subject, lesson_time, comment)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                created_at,
                form["name"],
                form["contact"],
                form["subject"],
                form["lesson_time"],
                form["comment"],
            ),
        )


def send_to_telegram(form: dict[str, str], token: str, chat_id: str) -> bool:
    if not token or not chat_id:
        return False

    text = (
        "📚 Новая заявка на занятие\n"
        f"Имя: {form['name']}\n"
        f"Контакт: {form['contact']}\n"
        f"Предмет: {form['subject']}\n"
        f"Время: {form['lesson_time']}\n"
        f"Комментарий: {form['comment'] or '-'}"
    )

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload: dict[str, Any] = {"chat_id": chat_id, "text": text}
    try:
        response = requests.post(url, json=payload, timeout=8)
        response.raise_for_status()
        data = response.json()
        return bool(data.get("ok"))
    except requests.RequestException:
        return False


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
