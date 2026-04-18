import sqlite3
import os
import json

os.makedirs("data", exist_ok=True)

conn = sqlite3.connect("data/users.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT,
    app TEXT,
    signature TEXT,
    has_secret INTEGER,
    PRIMARY KEY (username, app)
)
""")

conn.commit()

def save_user(username, app, signature, has_secret):
    cursor.execute(
        "INSERT OR REPLACE INTO users VALUES (?, ?, ?, ?)",
        (username, app, json.dumps(signature), has_secret)
    )
    conn.commit()

def get_user(username, app):
    cursor.execute(
        "SELECT signature, has_secret FROM users WHERE username=? AND app=?",
        (username, app)
    )
    row = cursor.fetchone()

    if row:
        return json.loads(row[0]), row[1]

    return None