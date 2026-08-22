from fractions import Fraction

import av
import cv2
from pathlib import Path
from ai.model_loader import load_model


class VideoDecodeError(RuntimeError):
    """Raised when the input video can't be opened or decoded."""


class VideoDetector:

    def __init__(self):
        self.model = load_model()

    def process_video(self, input_path, output_path, confidence=0.5):

        cap = cv2.VideoCapture(input_path)

        if not cap.isOpened():
            raise VideoDecodeError(
                f"Could not open video file: {input_path}. "
                "It may be corrupt or use an unsupported codec."
            )

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS) or 25.0

        if width <= 0 or height <= 0:
            cap.release()
            raise VideoDecodeError(
                f"Video reports invalid dimensions ({width}x{height}): {input_path}"
            )

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # Encode with H.264 via PyAV, not cv2.VideoWriter's default
        # "mp4v" fourcc - browsers (and so Streamlit's st.video, which
        # just embeds an HTML5 <video> tag) can't decode mp4v/MPEG-4
        # Part 2, so a mp4v-written .mp4 uploads and "processes" fine
        # but never actually plays back.
        try:
            container = av.open(output_path, mode="w")
            stream = container.add_stream("libx264", rate=Fraction(fps).limit_denominator())
            stream.width = width
            stream.height = height
            stream.pix_fmt = "yuv420p"
        except Exception as exc:
            cap.release()
            raise VideoDecodeError(
                f"Could not open video writer for output: {output_path} ({exc})"
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

            av_frame = av.VideoFrame.from_ndarray(annotated, format="bgr24")
            for packet in stream.encode(av_frame):
                container.mux(packet)

        cap.release()

        for packet in stream.encode():
            container.mux(packet)
        container.close()

        unique_defect_count = len(seen_track_ids)

        return output_path, detection_count, total_frames, unique_defect_count