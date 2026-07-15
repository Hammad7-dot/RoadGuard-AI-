import sqlite3
from pathlib import Path

DB_PATH = Path("database/roadguard.db")


def get_connection():

    DB_PATH.parent.mkdir(exist_ok=True)

    conn = sqlite3.connect(DB_PATH)

    conn.row_factory = sqlite3.Row

    return conn


def create_tables():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS detections(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        filename TEXT,

        damage_type TEXT,

        confidence REAL,

        x1 INTEGER,
        y1 INTEGER,
        x2 INTEGER,
        y2 INTEGER,

        detection_count INTEGER,

        processing_time REAL,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    )
    """)

    conn.commit()

    conn.close()


create_tables()