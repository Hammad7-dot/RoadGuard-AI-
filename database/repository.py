from database.database import get_connection


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

        processing_time

    ):

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute("""

        INSERT INTO detections(

        filename,

        damage_type,

        confidence,

        x1,

        y1,

        x2,

        y2,

        detection_count,

        processing_time

        )

        VALUES(?,?,?,?,?,?,?,?,?)

        """,

        (

        filename,

        damage_type,

        confidence,

        x1,

        y1,

        x2,

        y2,

        detection_count,

        processing_time

        )

        )

        conn.commit()

        conn.close()

    # ----------------------------

    def get_all(self):

        conn = get_connection()

        rows = conn.execute("""

        SELECT *

        FROM detections

        ORDER BY id DESC

        """).fetchall()

        conn.close()

        return rows

    # ----------------------------

    def total_detections(self):

        conn = get_connection()

        value = conn.execute("""

        SELECT COUNT(*)

        FROM detections

        """).fetchone()[0]

        conn.close()

        return value

    # ----------------------------

    def delete(self, record_id):

        conn = get_connection()

        conn.execute(

            "DELETE FROM detections WHERE id=?",

            (record_id,)

        )

        conn.commit()

        conn.close()
    
    def save_video_session(
        self,
        filename,
        total_frames,
        detections,
        processing_time,
        unique_defect_count=0

        ):

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute(
            """
        INSERT INTO detections(

            filename,

            damage_type,

            confidence,

            x1,

            y1,

            x2,

            y2,

            detection_count,

            processing_time,

            total_frames,

            unique_defect_count

        )

            VALUES(?,?,?,?,?,?,?,?,?,?,?)
            """,
            (

            filename,

            "Video Analysis",

            1.0,

            0,

            0,

            0,

            0,

            detections,

            processing_time,

            total_frames,

            unique_defect_count

            )
            )

        conn.commit()

        conn.close()

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
          + aggregated detections found in videos
        - avg_confidence: mean confidence over real image detections
          only (video session rows store a dummy confidence of 1.0
          since there's no per-object confidence for a whole video)
        """

        conn = get_connection()

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

        image_object_count = conn.execute("""
            SELECT COUNT(*)
            FROM detections
            WHERE damage_type != 'Video Analysis'
        """).fetchone()[0]

        video_detection_sum = conn.execute("""
            SELECT COALESCE(SUM(detection_count), 0)
            FROM detections
            WHERE damage_type = 'Video Analysis'
        """).fetchone()[0]

        avg_confidence_row = conn.execute("""
            SELECT AVG(confidence)
            FROM detections
            WHERE damage_type != 'Video Analysis'
        """).fetchone()[0]

        conn.close()

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

    def get_damage_distribution(self):
        """
        Real per-class counts for the dashboard chart, taken only
        from actual image detections (video session rows use the
        placeholder damage_type "Video Analysis" and would otherwise
        pollute this breakdown).
        """

        conn = get_connection()

        rows = conn.execute("""
            SELECT damage_type, COUNT(*) as count
            FROM detections
            WHERE damage_type != 'Video Analysis'
            GROUP BY damage_type
            ORDER BY count DESC
        """).fetchall()

        conn.close()

        return {row["damage_type"]: row["count"] for row in rows}