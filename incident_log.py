import sqlite3
from datetime import datetime


DB_PATH = "incidents.db"


def init_db(path=DB_PATH):
    conn = sqlite3.connect(path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            incident_type TEXT NOT NULL,
            metric_value TEXT,
            action_taken TEXT
        )
    """)
    conn.commit()
    conn.close()


def log_incident(incident_type, metric_value, action_taken, path=DB_PATH):
    init_db(path)
    conn = sqlite3.connect(path)
    conn.execute(
        "INSERT INTO incidents (timestamp, incident_type, metric_value, action_taken) VALUES (?, ?, ?, ?)",
        (datetime.now().isoformat(), incident_type, str(metric_value), action_taken)
    )
    conn.commit()
    conn.close()


def get_recent_incidents(limit=20, path=DB_PATH):
    conn = sqlite3.connect(path)
    cursor = conn.execute(
        "SELECT timestamp, incident_type, metric_value, action_taken FROM incidents ORDER BY id DESC LIMIT ?",
        (limit,)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


if __name__ == "__main__":
    for row in get_recent_incidents():
        print(row)
