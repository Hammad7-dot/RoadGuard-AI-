import unittest

from ai.detector import RoadDamageDetector


class RoadDamageDetectorMetricsTest(unittest.TestCase):
    def test_detection_summary_counts_classes(self):
        detections = [
            {"Class": "Pothole", "Confidence": 0.9},
            {"Class": "Crack", "Confidence": 0.7},
            {"Class": "Pothole", "Confidence": 0.8},
        ]

        self.assertEqual(
            RoadDamageDetector.detection_summary(detections),
            {"Pothole": 2, "Crack": 1},
        )

    def test_average_confidence_rounds_to_three_decimals(self):
        detections = [
            {"Class": "Pothole", "Confidence": 0.9123},
            {"Class": "Crack", "Confidence": 0.4567},
        ]

        self.assertEqual(
            RoadDamageDetector.average_confidence(detections),
            0.684,
        )

    def test_average_confidence_is_zero_for_empty_detections(self):
        self.assertEqual(RoadDamageDetector.average_confidence([]), 0.0)

    def test_total_objects_counts_detections(self):
        self.assertEqual(
            RoadDamageDetector.total_objects([{"Class": "Pothole"}, {"Class": "Crack"}]),
            2,
        )


if __name__ == "__main__":
    unittest.main()
