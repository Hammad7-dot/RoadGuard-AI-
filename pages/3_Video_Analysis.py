import os
import time
import streamlit as st

from ai.video_detector import VideoDetector
from database.repository import DetectionRepository
from components.sidebar import Sidebar
from utils.styles import load_css

# ---------------------------------------------------
# Page Config
# ---------------------------------------------------

st.set_page_config(
    page_title="Video Analysis",
    page_icon="🎥",
    layout="wide"
)

load_css()
Sidebar().render()

st.title("🎥 Video Analysis")
st.caption("Upload a road video for AI-powered road damage detection.")

# ---------------------------------------------------
# Upload Video
# ---------------------------------------------------

video = st.file_uploader(
    "Upload Video",
    type=["mp4", "avi", "mov"]
)

confidence = st.slider(
    "Confidence Threshold",
    min_value=0.10,
    max_value=1.00,
    value=0.50,
    step=0.05
)

# ---------------------------------------------------
# Process Video
# ---------------------------------------------------

if video is not None:

    os.makedirs("uploads/videos", exist_ok=True)
    os.makedirs("outputs/videos", exist_ok=True)

    input_path = os.path.join(
        "uploads/videos",
        video.name
    )

    output_path = os.path.join(
        "outputs/videos",
        video.name
    )

    with open(input_path, "wb") as f:
        f.write(video.read())

    if st.button("🚀 Start Detection", use_container_width=True):

        detector = VideoDetector()
        repo = DetectionRepository()

        progress = st.progress(0)
        status = st.empty()

        start_time = time.time()

        with st.spinner("Running YOLOv8..."):

            output_file, detection_count, total_frames, unique_defect_count = detector.process_video(
                input_path=input_path,
                output_path=output_path,
                confidence=confidence
            )

        processing_time = time.time() - start_time

        progress.progress(100)
        status.success("Video Processing Completed!")

        # ---------------------------------------
        # Save Detection Session
        # ---------------------------------------

        repo.save_video_session(
            filename=video.name,
            total_frames=total_frames,
            detections=detection_count,
            processing_time=processing_time,
            unique_defect_count=unique_defect_count
        )

        # ---------------------------------------
        # Statistics
        # ---------------------------------------

        fps = (
            total_frames / processing_time
            if processing_time > 0
            else 0
        )

        c1, c2, c3, c4, c5 = st.columns(5)

        c1.metric(
            "Frames",
            total_frames
        )

        c2.metric(
            "Detections",
            detection_count
        )

        c3.metric(
            "Unique Defects",
            unique_defect_count
        )

        c4.metric(
            "Processing Time",
            f"{processing_time:.2f}s"
        )

        c5.metric(
            "Average FPS",
            f"{fps:.1f}"
        )

        st.divider()

        st.subheader("Processed Video")

        st.video(output_file)

        with open(output_file, "rb") as file:

            st.download_button(
                "⬇ Download Processed Video",
                file,
                file_name=f"processed_{video.name}",
                mime="video/mp4",
                use_container_width=True
            )