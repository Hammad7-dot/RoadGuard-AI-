from database.database import db_connection


class DetectionRepository:

    def save_detection(
        self,
        filename,
        damage_type,
        confidence,
        x1,
        y1,
        x2,
        y2,
        detection_count,
        processing_time,
        latitude=None,
        longitude=None
    ):

        with db_connection() as conn:

            conn.execute(
                """
                INSERT INTO detections(
                    filename, damage_type, confidence,
                    x1, y1, x2, y2,
                    detection_count, processing_time,
                    latitude, longitude
                )
                VALUES(?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    filename, damage_type, confidence,
                    x1, y1, x2, y2,
                    detection_count, processing_time,
                    latitude, longitude
                )
            )

            conn.commit()

    # ----------------------------

    def get_all(self):

        with db_connection() as conn:

            rows = conn.execute("""
                SELECT *
                FROM detections
                ORDER BY id DESC
            """).fetchall()

            # sqlite3.Row isn't a true Mapping as far as pandas is
            # concerned, so pd.DataFrame(rows) silently drops the column
            # names and falls back to integer columns (0, 1, 2, ...).
            # Converting to plain dicts here keeps column names intact
            # for any caller that builds a DataFrame from this.
            return [dict(row) for row in rows]

    # ----------------------------

    def total_detections(self):

        with db_connection() as conn:

            value = conn.execute("""
                SELECT COUNT(*)
                FROM detections
            """).fetchone()[0]

            return value

    # ----------------------------

    def save_no_damage(self, filename, processing_time):
        """
        Log an image that was analyzed but had zero detections.

        BUG (fixed): previously, pages/2_Upload_Analysis.py only ever
        called save_detection() inside `for item in detections`, so a
        clean image (0 detections) produced zero rows — meaning it
        was invisible to get_dashboard_stats()'s "images_analyzed"
        distinct-filename count, to Recent Activity, and to the
        Reports history/CSV. A road survey full of undamaged photos
        looked identical to a survey that was never run. This inserts
        a real row (confidence/x1..y2 left NULL, detection_count=0)
        so the image is counted as analyzed without being counted as
        a detected defect.
        """

        with db_connection() as conn:

            conn.execute(
                """
                INSERT INTO detections(
                    filename,
                    damage_type,
                    detection_count,
                    processing_time
                )
                VALUES(?,?,?,?)
                """,
                (
                    filename,
                    "No Damage Detected",
                    0,
                    processing_time,
                ),
            )

            conn.commit()

    # ----------------------------

    def delete(self, record_id):

        with db_connection() as conn:

            conn.execute(
                "DELETE FROM detections WHERE id=?",
                (record_id,)
            )

            conn.commit()

    def save_video_session(
        self,
        filename,
        total_frames,
        detections,
        processing_time,
        unique_defect_count=0
    ):
        """
        Log an aggregate per-video row rather than one row per
        detected object (there's no stable per-object identity across
        frames for the whole session). confidence/x1..y2 are left
        NULL rather than filled with placeholder values (previously
        1.0 / 0 / 0 / 0 / 0) - those aren't real measurements for a
        video-level row, and a fake confidence of 1.0 would silently
        skew any query on this table that doesn't explicitly exclude
        damage_type == 'Video Analysis'.
        """

        with db_connection() as conn:

            conn.execute(
                """
                INSERT INTO detections(
                    filename,
                    damage_type,
                    detection_count,
                    processing_time,
                    total_frames,
                    unique_defect_count
                )
                VALUES(?,?,?,?,?,?)
                """,
                (
                    filename,
                    "Video Analysis",
                    detections,
                    processing_time,
                    total_frames,
                    unique_defect_count
                )
            )

            conn.commit()

    # ----------------------------

    def get_dashboard_stats(self):
        """
        Real counts pulled from the detections table, used to replace
        the dashboard's previously-hardcoded demo numbers.

        - images_analyzed: distinct image filenames processed
          (image rows are one-row-per-detected-object, so COUNT(*)
          would overcount; use distinct filenames instead)
        - videos_analyzed: one row per video session
          (damage_type == "Video Analysis")
        - total_detections: individual objects found in images
          + aggregated detections found in videos ("No Damage
          Detected" rows contribute 0, since they exist only to mark
          an image as analyzed and hold no real object)
        - avg_confidence: mean confidence over real image detections
          only (video session rows store NULL confidence since
          there's no per-object confidence for a whole video;
          "No Damage Detected" rows also store NULL confidence, which
          SQL AVG() already ignores)
        """

        with db_connection() as conn:

            # "images_analyzed" intentionally does NOT exclude
            # 'No Damage Detected' rows - those exist precisely so a
            # clean image still counts as analyzed.
            images_analyzed = conn.execute("""
                SELECT COUNT(DISTINCT filename)
                FROM detections
                WHERE damage_type != 'Video Analysis'
            """).fetchone()[0]

            videos_analyzed = conn.execute("""
                SELECT COUNT(*)
                FROM detections
                WHERE damage_type = 'Video Analysis'
            """).fetchone()[0]

            # Actual detected objects only - excludes both video session
            # rows and the zero-object "No Damage Detected" marker rows.
            image_object_count = conn.execute("""
                SELECT COUNT(*)
                FROM detections
                WHERE damage_type NOT IN ('Video Analysis', 'No Damage Detected')
            """).fetchone()[0]

            video_detection_sum = conn.execute("""
                SELECT COALESCE(SUM(detection_count), 0)
                FROM detections
                WHERE damage_type = 'Video Analysis'
            """).fetchone()[0]

            avg_confidence_row = conn.execute("""
                SELECT AVG(confidence)
                FROM detections
                WHERE damage_type NOT IN ('Video Analysis', 'No Damage Detected')
            """).fetchone()[0]

            return {
                "images_analyzed": images_analyzed,
                "videos_analyzed": videos_analyzed,
                "total_detections": image_object_count + video_detection_sum,
                "avg_confidence": (
                    round(avg_confidence_row, 3)
                    if avg_confidence_row is not None
                    else None
                ),
            }

    # ----------------------------

    def get_geotagged(self):
        """
        Detections that have GPS coordinates attached (either read
        from the image's EXIF data or entered manually on upload),
        for plotting on the Reports page map.
        """

        with db_connection() as conn:

            rows = conn.execute("""
                SELECT *
                FROM detections
                WHERE latitude IS NOT NULL AND longitude IS NOT NULL
                ORDER BY id DESC
            """).fetchall()

            return [dict(row) for row in rows]

    # ----------------------------

    def get_damage_distribution(self):
        """
        Real per-class counts for the dashboard chart, taken only
        from actual image detections (video session rows and the
        zero-object "No Damage Detected" marker rows use placeholder
        damage_type values and would otherwise pollute this
        breakdown).
        """

        with db_connection() as conn:

            rows = conn.execute("""
                SELECT damage_type, COUNT(*) as count
                FROM detections
                WHERE damage_type NOT IN ('Video Analysis', 'No Damage Detected')
                GROUP BY damage_type
                ORDER BY count DESC
            """).fetchall()

            return {row["damage_type"]: row["count"] for row in rows}
