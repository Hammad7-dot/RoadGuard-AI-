"""
RoadGuard AI
AI Detection Engine
-------------------

This module performs road damage detection using YOLOv8.
"""

from pathlib import Path
from typing import List, Dict, Tuple

import cv2
import numpy as np
from PIL import Image

from ai.model_loader import load_model


class RoadDamageDetector:
    """
    Road Damage Detection Engine
    """

    def __init__(self):

        self.model = load_model()

        self.class_names = self.model.names

    # ------------------------------------------------------

    def predict(
        self,
        image: Image.Image,
        confidence: float = 0.50
    ) -> Tuple[np.ndarray, List[Dict]]:

        """
        Run inference on a PIL image.

        Returns
        -------
        annotated_image
        detections
        """

        image_np = np.array(image)

        results = self.model.predict(

            source=image_np,

            conf=confidence,

            verbose=False

        )

        result = results[0]

        annotated_image = result.plot()

        detections = []

        if result.boxes is None:

            return annotated_image, detections

        for box in result.boxes:

            cls_id = int(box.cls.item())

            x1, y1, x2, y2 = box.xyxy[0].tolist()

            detections.append({

                "Class":
                    self.class_names[cls_id],

                "Confidence":
                    round(float(box.conf.item()), 3),

                "Bounding Box": {

                    "x1": int(x1),

                    "y1": int(y1),

                    "x2": int(x2),

                    "y2": int(y2)

                }

            })

        return annotated_image, detections

    # ------------------------------------------------------

    def save_output(

        self,

        image: np.ndarray,

        filename: str

    ) -> Path:

        """
        Save annotated image
        """

        output_dir = Path("outputs")

        output_dir.mkdir(exist_ok=True)

        output_path = output_dir / filename

        cv2.imwrite(

            str(output_path),

            cv2.cvtColor(

                image,

                cv2.COLOR_RGB2BGR

            )

        )

        return output_path

    # ------------------------------------------------------

    @staticmethod
    def detection_summary(
        detections: List[Dict]
    ) -> Dict:

        """
        Count each detected class.
        """

        summary = {}

        for detection in detections:

            cls = detection["Class"]

            summary[cls] = summary.get(cls, 0) + 1

        return summary

    # ------------------------------------------------------

    @staticmethod
    def average_confidence(
        detections: List[Dict]
    ) -> float:

        """
        Average confidence score.
        """

        if not detections:

            return 0.0

        return round(

            sum(

                d["Confidence"]

                for d in detections

            ) / len(detections),

            3

        )

    # ------------------------------------------------------

    @staticmethod
    def total_objects(
        detections: List[Dict]
    ) -> int:

        return len(detections)