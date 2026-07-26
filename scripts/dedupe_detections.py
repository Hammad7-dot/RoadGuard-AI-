"""
RoadGuard AI
Dedupe Detections
-------------------

One-off cleanup script for databases that picked up duplicate rows
from the Streamlit rerun bug (same image detected + saved multiple
times because every widget interaction re-ran the whole page).

A "duplicate" here means rows that share:
    filename, damage_type, confidence, x1, y1, x2, y2, processing_time
Real distinct detections will basically never collide on all of
these at once (processing_time alone is a float with millisecond
precision), so this is a safe signal for "this got inserted more
than once by the same rerun", not a false positive on legitimate
repeat inspections of the same spot.

Video-session rows (damage_type == "Video Analysis") are only
deduped on filename + total_frames + unique_defect_count, since they
don't have per-object bounding boxes.

USAGE
-----
    # Preview what would be deleted, without touching the DB:
    python scripts/dedupe_detections.py --dry-run

    # Actually delete the duplicates (keeps the earliest row in each
    # duplicate group, i.e. the lowest id):
    python scripts/dedupe_detections.py

A timestamped backup of the .db file is made automatically before
any deletion.
"""

import argparse
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path("database/roadguard.db")


def _get_columns(conn: sqlite3.Connection) -> set:
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(detections)")
    return {row[1] for row in cursor.fetchall()}


def find_duplicate_ids(conn: sqlite3.Connection) -> list:
    """
    Returns a list of row ids to delete: for every group of rows that
    are identical on the "duplicate signature" columns, keep the
    lowest id and mark the rest for deletion.
    """

    cursor = conn.cursor()
    columns = _get_columns(conn)

    ids_to_delete = []

    # ---- Image detections ----
    cursor.execute("""
        SELECT MIN(id) as keep_id, filename, damage_type, confidence,
               x1, y1, x2, y2, processing_time, COUNT(*) as cnt
        FROM detections
        WHERE damage_type != 'Video Analysis'
        GROUP BY filename, damage_type, confidence, x1, y1, x2, y2, processing_time
        HAVING cnt > 1
    """)
    image_groups = cursor.fetchall()

    for row in image_groups:
        keep_id, filename, damage_type, confidence, x1, y1, x2, y2, processing_time, cnt = row
        cursor.execute("""
            SELECT id FROM detections
            WHERE filename=? AND damage_type=? AND confidence=?
              AND x1=? AND y1=? AND x2=? AND y2=? AND processing_time=?
              AND id != ?
        """, (filename, damage_type, confidence, x1, y1, x2, y2, processing_time, keep_id))
        ids_to_delete.extend(r[0] for r in cursor.fetchall())

    # ---- Video sessions ----
    # Only attempted if this database has actually been migrated to
    # include total_frames / unique_defect_count (older databases,
    # or ones where the app's automatic migration hasn't run yet,
    # won't have these columns).
    if "total_frames" in columns and "unique_defect_count" in columns:
        cursor.execute("""
            SELECT MIN(id) as keep_id, filename, total_frames, unique_defect_count, COUNT(*) as cnt
            FROM detections
            WHERE damage_type = 'Video Analysis'
            GROUP BY filename, total_frames, unique_defect_count
            HAVING cnt > 1
        """)
        video_groups = cursor.fetchall()

        for row in video_groups:
            keep_id, filename, total_frames, unique_defect_count, cnt = row
            cursor.execute("""
                SELECT id FROM detections
                WHERE filename=? AND total_frames=? AND unique_defect_count=?
                  AND damage_type = 'Video Analysis' AND id != ?
            """, (filename, total_frames, unique_defect_count, keep_id))
            ids_to_delete.extend(r[0] for r in cursor.fetchall())
    else:
        # Fall back to filename + detection_count + processing_time,
        # which exist on every schema version, and still describe a
        # video session uniquely enough for dedup purposes.
        cursor.execute("""
            SELECT MIN(id) as keep_id, filename, detection_count, processing_time, COUNT(*) as cnt
            FROM detections
            WHERE damage_type = 'Video Analysis'
            GROUP BY filename, detection_count, processing_time
            HAVING cnt > 1
        """)
        video_groups = cursor.fetchall()

        for row in video_groups:
            keep_id, filename, detection_count, processing_time, cnt = row
            cursor.execute("""
                SELECT id FROM detections
                WHERE filename=? AND detection_count=? AND processing_time=?
                  AND damage_type = 'Video Analysis' AND id != ?
            """, (filename, detection_count, processing_time, keep_id))
            ids_to_delete.extend(r[0] for r in cursor.fetchall())

    return sorted(set(ids_to_delete))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would be deleted without modifying the database"
    )
    parser.add_argument(
        "--db", type=str, default=str(DB_PATH),
        help="Path to roadguard.db (default: database/roadguard.db)"
    )
    args = parser.parse_args()

    db_path = Path(args.db)

    if not db_path.exists():
        raise SystemExit(f"No database found at {db_path}")

    conn = sqlite3.connect(db_path)

    total_before = conn.execute("SELECT COUNT(*) FROM detections").fetchone()[0]

    ids_to_delete = find_duplicate_ids(conn)

    print(f"Total rows currently in database: {total_before}")
    print(f"Duplicate rows found: {len(ids_to_delete)}")
    print(f"Rows remaining after cleanup: {total_before - len(ids_to_delete)}")

    if not ids_to_delete:
        print("Nothing to clean up.")
        conn.close()
        return

    if args.dry_run:
        print("\n--dry-run passed, no changes made. "
              "Re-run without --dry-run to actually delete these rows.")
        conn.close()
        return

    # Backup before touching anything
    backup_path = db_path.with_name(
        f"{db_path.stem}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}{db_path.suffix}"
    )
    shutil.copy2(db_path, backup_path)
    print(f"\nBackup saved to: {backup_path}")

    cursor = conn.cursor()
    # SQLite has a default limit around 999-32766 host parameters
    # depending on build; chunk the delete to stay well under that
    # for very large duplicate sets.
    chunk_size = 500
    for i in range(0, len(ids_to_delete), chunk_size):
        chunk = ids_to_delete[i:i + chunk_size]
        placeholders = ",".join("?" for _ in chunk)
        cursor.execute(f"DELETE FROM detections WHERE id IN ({placeholders})", chunk)

    conn.commit()
    conn.close()

    print(f"Deleted {len(ids_to_delete)} duplicate rows. Done.")


if __name__ == "__main__":
    main()