import time
import pandas as pd
import streamlit as st
from PIL import Image

from components.sidebar import Sidebar
from components.detection_summary import detection_summary
from utils.styles import load_css
from ai.detector import RoadDamageDetector
from database.repository import DetectionRepository

# --------------------------------------------------
# Page Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Upload Analysis",
    page_icon="📤",
    layout="wide"
)

load_css()
Sidebar().render()

# --------------------------------------------------
# Title
# --------------------------------------------------

st.title("📤 Upload Road Image")
st.caption("Upload a road image and let YOLOv8 detect road damages.")

# --------------------------------------------------
# Upload Section
# --------------------------------------------------

uploaded_file = st.file_uploader(
    "Choose an image",
    type=["jpg", "jpeg", "png"]
)

confidence = st.slider(
    "Confidence Threshold",
    min_value=0.10,
    max_value=1.00,
    value=0.50,
    step=0.05
)

# --------------------------------------------------
# Detection
# --------------------------------------------------

if uploaded_file is not None:

    image = Image.open(uploaded_file).convert("RGB")

    detector = RoadDamageDetector()

    start = time.time()

    annotated_image, detections = detector.predict(
        image=image,
        confidence=confidence
    )

    processing_time = time.time() - start

    # ---------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("📷 Original Image")

        st.image(
            image,
            use_container_width=True
        )

    with col2:

        st.subheader("🤖 Detection Result")

        st.image(
            annotated_image,
            use_container_width=True
        )

    # ---------------------------------------------
    # Metrics
    # ---------------------------------------------

    total_objects = detector.total_objects(detections)

    avg_confidence = detector.average_confidence(detections)

    m1, m2, m3 = st.columns(3)

    m1.metric(
        "Objects Detected",
        total_objects
    )

    m2.metric(
        "Average Confidence",
        f"{avg_confidence*100:.1f}%"
    )

    m3.metric(
        "Processing Time",
        f"{processing_time:.2f} sec"
    )

    st.divider()

    # ---------------------------------------------
    # Detection Details
    # ---------------------------------------------

    st.subheader("📋 Detection Details")

    if detections:

        table = []

        for item in detections:

            table.append({

                "Damage Type":
                    item["Class"],

                "Confidence":
                    f"{item['Confidence']*100:.1f}%",

                "X1":
                    item["Bounding Box"]["x1"],

                "Y1":
                    item["Bounding Box"]["y1"],

                "X2":
                    item["Bounding Box"]["x2"],

                "Y2":
                    item["Bounding Box"]["y2"]

            })

        st.dataframe(
            pd.DataFrame(table),
            use_container_width=True,
            hide_index=True
        )

    else:

        st.warning("No road damage detected.")

    st.divider()

    # ---------------------------------------------
    # Step 6
    # ---------------------------------------------

    summary = detector.detection_summary(detections)

    detection_summary(summary)

    # ---------------------------------------------
    # Download
    # ---------------------------------------------

    output_path = detector.save_output(
        annotated_image,
        "prediction.jpg"
    )

    with open(output_path, "rb") as file:

        st.download_button(
            "⬇ Download Result",
            file,
            file_name="road_damage_prediction.jpg",
            mime="image/jpeg"
        )

    # ---------------------------------------------
    # Save to database
    # ---------------------------------------------

    repo = DetectionRepository()

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
            processing_time=processing_time
        )