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

        total_frames INTEGER,

        unique_defect_count INTEGER,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    )
    """)

    conn.commit()

    conn.close()


def _migrate_schema():
    """
    Add new columns to an existing detections table for people who
    already have a roadguard.db from before total_frames /
    unique_defect_count existed. SQLite has no "ADD COLUMN IF NOT
    EXISTS", so check pragma info first.
    """

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(detections)")

    existing_columns = {row[1] for row in cursor.fetchall()}

    if "total_frames" not in existing_columns:
        cursor.execute(
            "ALTER TABLE detections ADD COLUMN total_frames INTEGER"
        )

    if "unique_defect_count" not in existing_columns:
        cursor.execute(
            "ALTER TABLE detections ADD COLUMN unique_defect_count INTEGER"
        )

    conn.commit()

    conn.close()


create_tables()
_migrate_schema()
