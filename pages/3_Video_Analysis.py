import hashlib
import os
import time
import streamlit as st

from ai.video_detector import VideoDetector, VideoDecodeError
from database.repository import DetectionRepository
from components.confidence_slider import confidence_slider
from utils.page import init_page

# ---------------------------------------------------
# Page Config
# ---------------------------------------------------

init_page("Video Analysis", "🎥")

st.title("🎥 Video Analysis")
st.caption("Upload a road video for AI-powered road damage detection.")

# ---------------------------------------------------
# Upload Video
# ---------------------------------------------------

video = st.file_uploader(
    "Upload Video",
    type=["mp4", "avi", "mov"]
)

confidence = confidence_slider(key="video_confidence")

# ---------------------------------------------------
# Process Video
# ---------------------------------------------------

if "video_cache" not in st.session_state:
    st.session_state.video_cache = {}

CACHE = st.session_state.video_cache

if video is not None:

    os.makedirs("uploads/videos", exist_ok=True)
    os.makedirs("outputs/videos", exist_ok=True)

    # Keyed on content hash + confidence, not just the filename, so
    # two different uploads that happen to share a name don't
    # overwrite each other's output on disk, and moving the
    # confidence slider or re-running the script doesn't re-write the
    # file or re-run detection unnecessarily.
    content_hash = hashlib.md5(video.getvalue()).hexdigest()[:12]
    video_key = f"{content_hash}_{confidence}"

    safe_stem = video.name.rsplit(".", 1)[0]
    unique_name = f"{safe_stem}_{content_hash}.mp4"

    input_path = os.path.join("uploads/videos", f"{content_hash}_{video.name}")
    output_path = os.path.join("outputs/videos", unique_name)

    if video_key not in CACHE:
        with open(input_path, "wb") as f:
            f.write(video.getvalue())

    if st.button("🚀 Start Detection", use_container_width=True):

        if video_key in CACHE:
            # Already processed this exact file+confidence combo -
            # reuse the cached result instead of re-running inference
            # and writing a duplicate database row.
            cached = CACHE[video_key]
            output_file = cached["output_file"]
            detection_count = cached["detection_count"]
            total_frames = cached["total_frames"]
            unique_defect_count = cached["unique_defect_count"]
            processing_time = cached["processing_time"]
            st.info("Already processed - showing cached result.")
        else:
            detector = VideoDetector()
            repo = DetectionRepository()

            progress = st.progress(0)
            status = st.empty()

            start_time = time.time()

            try:
                with st.spinner("Running YOLOv8..."):

                    output_file, detection_count, total_frames, unique_defect_count = detector.process_video(
                        input_path=input_path,
                        output_path=output_path,
                        confidence=confidence
                    )
            except VideoDecodeError as exc:
                st.error(f"Could not process this video: {exc}")
                st.stop()

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

            CACHE[video_key] = {
                "output_file": output_file,
                "detection_count": detection_count,
                "total_frames": total_frames,
                "unique_defect_count": unique_defect_count,
                "processing_time": processing_time,
            }

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