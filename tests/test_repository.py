import tempfile
import unittest
from pathlib import Path

import database.database as db_module
from database.repository import DetectionRepository


class DetectionRepositoryTest(unittest.TestCase):
    """
    Uses a throwaway temp-file database for each test (never the real
    database/roadguard.db), per RULES.md R17.
    """

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self._original_db_path = db_module.DB_PATH
        db_module.DB_PATH = Path(self._tmpdir.name) / "test.db"
        db_module.create_tables()
        db_module._migrate_schema()
        self.repo = DetectionRepository()

    def tearDown(self):
        db_module.DB_PATH = self._original_db_path
        self._tmpdir.cleanup()

    def test_get_all_empty_returns_empty_list(self):
        self.assertEqual(self.repo.get_all(), [])

    def test_get_dashboard_stats_on_empty_db(self):
        stats = self.repo.get_dashboard_stats()
        self.assertEqual(stats["images_analyzed"], 0)
        self.assertEqual(stats["videos_analyzed"], 0)
        self.assertEqual(stats["total_detections"], 0)
        self.assertIsNone(stats["avg_confidence"])

    def test_save_no_damage_counts_as_image_analyzed_not_detection(self):
        self.repo.save_no_damage("clean.jpg", processing_time=0.1)

        stats = self.repo.get_dashboard_stats()

        self.assertEqual(stats["images_analyzed"], 1)
        self.assertEqual(stats["total_detections"], 0)

    def test_save_video_session_stores_null_confidence_and_bbox(self):
        self.repo.save_video_session(
            filename="road.mp4",
            total_frames=100,
            detections=5,
            processing_time=2.0,
            unique_defect_count=3,
        )

        rows = self.repo.get_all()

        self.assertEqual(len(rows), 1)
        self.assertIsNone(rows[0]["confidence"])
        self.assertIsNone(rows[0]["x1"])
        self.assertEqual(rows[0]["detection_count"], 5)

    def test_video_session_excluded_from_damage_distribution(self):
        self.repo.save_video_session(
            filename="road.mp4",
            total_frames=10,
            detections=2,
            processing_time=1.0,
        )
        self.repo.save_detection(
            filename="pic.jpg",
            damage_type="Pothole",
            confidence=0.9,
            x1=0, y1=0, x2=10, y2=10,
            detection_count=1,
            processing_time=0.5,
        )

        distribution = self.repo.get_damage_distribution()

        self.assertEqual(distribution, {"Pothole": 1})

    def test_delete_removes_record(self):
        self.repo.save_no_damage("a.jpg", 0.1)
        record_id = self.repo.get_all()[0]["id"]

        self.repo.delete(record_id)

        self.assertEqual(self.repo.get_all(), [])


if __name__ == "__main__":
    unittest.main()
