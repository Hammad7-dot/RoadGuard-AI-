import cv2
from pathlib import Path
from ai.model_loader import load_model


class VideoDetector:

    def __init__(self):
        self.model = load_model()

    def process_video(self, input_path, output_path, confidence=0.5):

        cap = cv2.VideoCapture(input_path)

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS) or 25.0

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        writer = cv2.VideoWriter(
            output_path,
            cv2.VideoWriter_fourcc(*"mp4v"),
            fps,
            (width, height)
        )

        detection_count = 0
        total_frames = 0
        seen_track_ids = set()

        # persist=True keeps ByteTrack's internal state alive across
        # calls so the same pothole/crack keeps the same ID as it
        # moves through consecutive frames instead of being detected
        # fresh (and re-counted) every single frame.
        self.model.predictor = None  # reset any tracker state from a previous video

        while True:

            success, frame = cap.read()

            if not success:
                break

            total_frames += 1

            results = self.model.track(
                frame,
                conf=confidence,
                persist=True,
                tracker="bytetrack.yaml",
                verbose=False
            )

            result = results[0]
            annotated = result.plot()

            if result.boxes is not None:
                detection_count += len(result.boxes)
                if result.boxes.id is not None:
                    for track_id in result.boxes.id.tolist():
                        seen_track_ids.add(int(track_id))

            writer.write(annotated)

        cap.release()
        writer.release()

        unique_defect_count = len(seen_track_ids)

        return output_path, detection_count, total_frames, unique_defect_count