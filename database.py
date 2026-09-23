import sqlite3
from contextlib import closing

from config import DB_PATH


def init_db():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        with conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER NOT NULL,
                    username TEXT,
                    region TEXT,
                    subject TEXT,
                    full_name TEXT,
                    experience TEXT,
                    certificate_file_id TEXT,
                    diploma_file_id TEXT,
                    phone TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )


def add_registration(data: dict):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        with conn:
            conn.execute(
                """
                INSERT INTO users (
                    telegram_id, username, region, subject, full_name,
                    experience, certificate_file_id, diploma_file_id, phone
                ) VALUES (
                    :telegram_id, :username, :region, :subject, :full_name,
                    :experience, :certificate_file_id, :diploma_file_id, :phone
                )
                """,
                data,
            )


def get_all_registrations():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute("SELECT * FROM users ORDER BY id DESC")
        return cur.fetchall()


def count_registrations() -> int:
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.execute("SELECT COUNT(*) FROM users")
        return cur.fetchone()[0]
