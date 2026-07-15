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
        processing_time
    
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

            processing_time

        )

            VALUES(?,?,?,?,?,?,?,?,?)
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

            processing_time

            )
            )

        conn.commit()

        conn.close()