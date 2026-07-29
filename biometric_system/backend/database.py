import sqlite3
import os
import json

os.makedirs("data", exist_ok=True)

conn = sqlite3.connect(
    "data/users.db",
    check_same_thread=False
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    username TEXT,
    app TEXT,

    signature TEXT,
    seed TEXT,

    has_secret INTEGER
)
""")

conn.commit()


def save_user(
    username,
    app,
    signature,
    seed,
    has_secret
):

    cursor.execute(
        """
        INSERT INTO users
        (
            username,
            app,
            signature,
            seed,
            has_secret
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            username,
            app,
            json.dumps(signature),
            seed.hex(),
            has_secret
        )
    )

    conn.commit()


def get_users(username, app):

    cursor.execute(
        """
        SELECT signature, seed, has_secret
        FROM users
        WHERE username=? AND app=?
        """,
        (username, app)
    )

    rows = cursor.fetchall()

    users = []

    for row in rows:

        users.append(
            (
                json.loads(row[0]),
                bytes.fromhex(row[1]),
                row[2]
            )
        )

    return users