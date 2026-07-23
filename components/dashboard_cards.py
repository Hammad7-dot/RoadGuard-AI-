import streamlit as st

from database.repository import DetectionRepository


def dashboard_cards():

    st.subheader("Overview")

    stats = DetectionRepository().get_dashboard_stats()

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Images",
        stats["images_analyzed"]
    )

    c2.metric(
        "Videos",
        stats["videos_analyzed"]
    )

    c3.metric(
        "Detections",
        stats["total_detections"]
    )

    c4.metric(
        "Avg. Confidence",
        f"{stats['avg_confidence'] * 100:.1f}%"
        if stats["avg_confidence"] is not None
        else "N/A"
    )