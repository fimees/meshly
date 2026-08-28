import sqlite3
from datetime import datetime, timezone

from .auth import hash_password, verify_password


class Database:

    def __init__(self, path: str):
        self.path = path

        self.init()

    def connect(self):
        return sqlite3.connect(
            self.path,
            check_same_thread=False,
        )

    def init(self):

        db = self.connect()

        db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        db.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                room TEXT NOT NULL,
                text TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        db.commit()
        db.close()

    def register(
        self,
        username: str,
        password: str,
    ) -> bool:

        password_hash, salt = hash_password(
            password
        )

        db = self.connect()

        try:

            db.execute(
                """
                INSERT INTO users
                (username, password_hash, salt, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (
                    username,
                    password_hash,
                    salt,
                    datetime.now(
                        timezone.utc
                    ).isoformat(),
                ),
            )

            db.commit()

            return True

        except sqlite3.IntegrityError:

            return False

        finally:

            db.close()

    def login(
        self,
        username: str,
        password: str,
    ) -> bool:

        db = self.connect()

        row = db.execute(
            """
            SELECT password_hash, salt
            FROM users
            WHERE username = ?
            """,
            (username,),
        ).fetchone()

        db.close()

        if row is None:
            return False

        password_hash, salt = row

        return verify_password(
            password,
            password_hash,
            salt,
        )

    def save_message(
        self,
        username: str,
        room: str,
        text: str,
    ):

        db = self.connect()

        db.execute(
            """
            INSERT INTO messages
            (username, room, text, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (
                username,
                room,
                text,
                datetime.now(
                    timezone.utc
                ).isoformat(),
            ),
        )

        db.commit()
        db.close()

    def history(
        self,
        room: str,
        limit: int = 50,
    ):

        db = self.connect()

        rows = db.execute(
            """
            SELECT username, text, created_at
            FROM messages
            WHERE room = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (room, limit),
        ).fetchall()

        db.close()

        return list(reversed(rows))
