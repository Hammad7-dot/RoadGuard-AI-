"""
RoadGuard AI
Live Camera Detector
---------------------

Two ways to run detection against a live camera:

1. `WebcamDetector.predict_frame` - single-shot inference on a frame
   captured via the browser's camera (st.camera_input). Good for
   "snapshot" style analysis.

2. `LiveVideoProcessor` - a streamlit-webrtc VideoProcessorBase that
   receives a continuous stream of frames from the browser's camera
   and annotates each one in real time, so the user sees live,
   moving video with detections instead of a single still photo.
   This works both locally and on cloud deployments, unlike a raw
   cv2.VideoCapture(0) + cv2.imshow() loop, which needs direct
   OS-level webcam/GUI access that a server (and
   opencv-python-headless, which this project depends on) does not
   have.
"""

import time

import numpy as np
from PIL import Image

from ai.model_loader import load_model

try:
    import av
    from streamlit_webrtc import VideoProcessorBase
except ImportError:  # streamlit-webrtc/av not installed yet
    av = None
    VideoProcessorBase = object


class WebcamDetector:

    def __init__(self):
        self.model = load_model()

    def predict_frame(self, image: Image.Image, confidence: float = 0.5):
        """
        Run inference on a single captured frame.

        Returns
        -------
        annotated_image
        detection_count
        """

        image_np = np.array(image.convert("RGB"))

        results = self.model.predict(
            source=image_np,
            conf=confidence,
            verbose=False
        )

        result = results[0]
        annotated_image = result.plot()

        detection_count = len(result.boxes) if result.boxes is not None else 0

        return annotated_image, detection_count


class LiveVideoProcessor(VideoProcessorBase):
    """
    Real-time video processor for streamlit-webrtc.

    Each incoming frame from the browser's live camera stream is run
    through YOLOv8 **tracking** (ByteTrack, via Ultralytics'
    `model.track(..., persist=True)`) rather than plain per-frame
    detection. This assigns each pothole/crack a persistent track ID
    that stays the same across frames, so the same defect isn't
    re-counted every frame as the camera moves - giving both live
    annotated video AND a running count of unique road defects seen.
    """

    def __init__(self):
        self.model = load_model()
        self.confidence = 0.5
        self.last_detection_count = 0
        self.last_fps = 0.0
        self.seen_track_ids = set()

    def set_confidence(self, confidence: float):
        self.confidence = confidence

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")

        start = time.time()

        results = self.model.track(
            source=img,
            conf=self.confidence,
            persist=True,       # keep track state between calls
            tracker="bytetrack.yaml",
            verbose=False
        )

        result = results[0]
        annotated = result.plot()  # BGR ndarray with boxes + track IDs drawn

        if result.boxes is not None:
            self.last_detection_count = len(result.boxes)
            if result.boxes.id is not None:
                for track_id in result.boxes.id.tolist():
                    self.seen_track_ids.add(int(track_id))
        else:
            self.last_detection_count = 0

        elapsed = time.time() - start
        self.last_fps = 1.0 / elapsed if elapsed > 0 else 0.0

        return av.VideoFrame.from_ndarray(annotated, format="bgr24")

    @property
    def unique_defect_count(self) -> int:
        """Total number of distinct tracked defects seen so far."""
        return len(self.seen_track_ids)
