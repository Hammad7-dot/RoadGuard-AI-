import hashlib
import time
import uuid

import pandas as pd
import streamlit as st
from PIL import Image

from components.detection_summary import detection_summary
from components.confidence_slider import confidence_slider
from utils.page import init_page
from ai.detector import RoadDamageDetector
from database.repository import DetectionRepository
from utils.geotag import extract_gps

# --------------------------------------------------
# Page Configuration
# --------------------------------------------------

init_page("Upload Analysis", "📤")

# --------------------------------------------------
# Title
# --------------------------------------------------

st.title("📤 Upload Road Image")
st.caption("Upload one or more road images and let YOLOv8 detect road damages.")

# --------------------------------------------------
# Severity scoring
# --------------------------------------------------
# Confidence alone doesn't tell you how bad a defect is - a small,
# faint crack and a huge, obvious pothole can both score 0.9
# confidence. Combining confidence with the detection's share of the
# frame gives a rough proxy for "how serious does this look", useful
# for triage (e.g. "fix High severity potholes first").


def _severity(confidence: float, box: dict, image_area: int) -> str:
    box_area = max(0, box["x2"] - box["x1"]) * max(0, box["y2"] - box["y1"])
    area_ratio = box_area / image_area if image_area else 0
    score = (confidence * 0.6) + (min(area_ratio * 10, 1.0) * 0.4)

    if score >= 0.65:
        return "🔴 High"
    if score >= 0.40:
        return "🟠 Medium"
    return "🟡 Low"


def _road_condition(severities: list) -> str:
    if not severities:
        return "🟢 Good"
    if any(s.startswith("🔴") for s in severities):
        return "🔴 Poor - urgent repair recommended"
    if any(s.startswith("🟠") for s in severities):
        return "🟠 Fair - monitor / schedule repair"
    return "🟡 Minor wear detected"


# --------------------------------------------------
# Upload Section
# --------------------------------------------------

uploaded_files = st.file_uploader(
    "Choose image(s)",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

confidence = confidence_slider(key="upload_confidence")

# --------------------------------------------------
# Session-state cache
# --------------------------------------------------
# Streamlit reruns this ENTIRE script top-to-bottom on every widget
# interaction (moving the confidence slider, toggling the location
# checkbox, nudging a lat/lon field, expanding a panel...). Without
# caching, that meant every rerun re-ran YOLO inference AND
# re-inserted the same detections into the database again - so a
# 3-image batch could log hundreds of duplicate rows just from the
# user opening a expander. `st.session_state` persists across
# reruns (as long as the file stays uploaded), so we use it to run
# detection + the DB save exactly once per unique file per
# confidence setting.

if "upload_cache" not in st.session_state:
    st.session_state.upload_cache = {}

CACHE = st.session_state.upload_cache

# --------------------------------------------------
# Detection
# --------------------------------------------------

if uploaded_files:

    detector = RoadDamageDetector()
    repo = DetectionRepository()

    # Batch-level rollup shown once at the top, then a per-image
    # breakdown below so a multi-photo road survey gets an
    # at-a-glance summary instead of scrolling through every image.
    batch_rows = []

    for uploaded_file in uploaded_files:

        # Keyed on content hash (not name+size, which two different
        # same-sized files with the same name would collide on) plus
        # confidence, so changing the slider re-runs detection (as it
        # should) but re-opening an expander or toggling GPS does not.
        content_hash = hashlib.md5(uploaded_file.getvalue()).hexdigest()[:12]
        file_key = f"{content_hash}_{confidence}"

        with st.expander(f"📷 {uploaded_file.name}", expanded=(len(uploaded_files) == 1)):

            raw_image = Image.open(uploaded_file)
            auto_gps = extract_gps(raw_image)
            image = raw_image.convert("RGB")
            image_area = image.width * image.height

            with st.expander("📍 Location (optional)", expanded=False):
                if auto_gps:
                    st.caption("Read from the photo's EXIF data. Adjust if needed.")
                default_lat, default_lon = auto_gps if auto_gps else (0.0, 0.0)
                use_location = st.checkbox(
                    "Attach GPS coordinates to this detection",
                    value=auto_gps is not None,
                    key=f"use_loc_{content_hash}"
                )
                lat_col, lon_col = st.columns(2)
                latitude = lat_col.number_input(
                    "Latitude", value=float(default_lat), format="%.6f",
                    key=f"lat_{content_hash}"
                )
                longitude = lon_col.number_input(
                    "Longitude", value=float(default_lon), format="%.6f",
                    key=f"lon_{content_hash}"
                )

            # ---------------------------------------------
            # Run detection only once per file+confidence combo.
            # Everything below reads from the cached result instead
            # of recomputing it, so widget interactions elsewhere on
            # the page don't trigger repeat inference or repeat
            # database writes.
            # ---------------------------------------------

            if file_key not in CACHE:
                start = time.time()

                annotated_image, detections = detector.predict(
                    image=image,
                    confidence=confidence
                )

                processing_time = time.time() - start

                for item in detections:
                    item["Severity"] = _severity(
                        item["Confidence"], item["Bounding Box"], image_area
                    )

                safe_stem = uploaded_file.name.rsplit(".", 1)[0]
                output_filename = f"{safe_stem}_{uuid.uuid4().hex[:8]}.jpg"
                output_path = detector.save_output(annotated_image, output_filename)

                CACHE[file_key] = {
                    "annotated_image": annotated_image,
                    "detections": detections,
                    "processing_time": processing_time,
                    "output_path": output_path,
                    "output_filename": output_filename,
                    "saved_to_db": False,
                }

            cached = CACHE[file_key]
            annotated_image = cached["annotated_image"]
            detections = cached["detections"]
            processing_time = cached["processing_time"]
            output_path = cached["output_path"]
            output_filename = cached["output_filename"]

            # ---------------------------------------------

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Original")
                st.image(image, use_container_width=True)

            with col2:
                st.subheader("Detection Result")
                st.image(annotated_image, use_container_width=True)

            # ---------------------------------------------
            # Metrics
            # ---------------------------------------------

            total_objects = detector.total_objects(detections)
            avg_confidence = detector.average_confidence(detections)
            condition = _road_condition([d["Severity"] for d in detections])

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Objects Detected", total_objects)
            m2.metric("Average Confidence", f"{avg_confidence * 100:.1f}%")
            m3.metric("Processing Time", f"{processing_time:.2f} sec")
            m4.metric("Road Condition", condition)

            # ---------------------------------------------
            # Detection Details
            # ---------------------------------------------

            st.subheader("📋 Detection Details")

            if detections:
                table = [
                    {
                        "Damage Type": item["Class"],
                        "Severity": item["Severity"],
                        "Confidence": f"{item['Confidence'] * 100:.1f}%",
                        "X1": item["Bounding Box"]["x1"],
                        "Y1": item["Bounding Box"]["y1"],
                        "X2": item["Bounding Box"]["x2"],
                        "Y2": item["Bounding Box"]["y2"],
                    }
                    for item in detections
                ]

                st.dataframe(
                    pd.DataFrame(table),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.warning("No road damage detected.")

            summary = detector.detection_summary(detections)
            detection_summary(summary)

            # ---------------------------------------------
            # Download
            # ---------------------------------------------

            with open(output_path, "rb") as file:
                st.download_button(
                    "⬇ Download Result",
                    file,
                    file_name=f"roadguard_{output_filename}",
                    mime="image/jpeg",
                    key=f"dl_{output_filename}"
                )

            # ---------------------------------------------
            # Save to database - only once per cached result, no
            # matter how many times this script reruns afterward.
            # ---------------------------------------------

            if not cached["saved_to_db"]:
                if detections:
                    for item in detections:
                        box = item["Bounding Box"]
                        repo.save_detection(
                            filename=uploaded_file.name,
                            damage_type=item["Class"],
                            confidence=item["Confidence"],
                            x1=box["x1"],
                            y1=box["y1"],
                            x2=box["x2"],
                            y2=box["y2"],
                            detection_count=len(detections),
                            processing_time=processing_time,
                            latitude=latitude if use_location else None,
                            longitude=longitude if use_location else None,
                        )
                else:
                    # BUG (fixed): a clean image with zero detections
                    # used to produce no DB row at all, making it
                    # invisible to "Images Analyzed", Recent Activity,
                    # and the Reports history/CSV. Log it explicitly.
                    repo.save_no_damage(
                        filename=uploaded_file.name,
                        processing_time=processing_time,
                    )
                cached["saved_to_db"] = True

            batch_rows.append({
                "Image": uploaded_file.name,
                "Objects": total_objects,
                "Avg Confidence": f"{avg_confidence * 100:.1f}%",
                "Condition": condition,
            })

    if len(uploaded_files) > 1:
        st.divider()
        st.subheader("📦 Batch Summary")
        st.dataframe(pd.DataFrame(batch_rows), use_container_width=True, hide_index=True)