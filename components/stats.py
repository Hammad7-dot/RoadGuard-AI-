import streamlit as st

from utils.constants import DAMAGE_CLASSES
from database.repository import DetectionRepository


def stats_section():

    st.markdown(
        "<h2 style='text-align:center;'>System Overview</h2>",
        unsafe_allow_html=True
    )

    stats = DetectionRepository().get_dashboard_stats()

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Damage Classes",
        str(len(DAMAGE_CLASSES))
    )

    c2.metric(
        "YOLO Model",
        "v8"
    )

    c3.metric(
        "Avg. Confidence",
        f"{stats['avg_confidence'] * 100:.1f}%"
        if stats["avg_confidence"] is not None
        else "N/A"
    )

    c4.metric(
        "Total Detections",
        stats["total_detections"]
    )