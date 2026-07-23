import streamlit as st
import pandas as pd

from database.repository import DetectionRepository


def recent_activity():

    st.subheader("Recent Activity")

    rows = DetectionRepository().get_all()

    # Only real image/video detections, most recent first, capped at 8
    # so the dashboard card doesn't grow unbounded.
    recent = [r for r in rows if r["damage_type"] != "Video Analysis"][:8]

    if not recent:
        st.info("No detections yet — run an analysis to see activity here.")
        return

    df = pd.DataFrame({
        "Time": [
            str(r["created_at"]).split(" ")[-1][:5]
            for r in recent
        ],
        "Damage": [r["damage_type"] for r in recent],
        "Confidence": [f"{r['confidence'] * 100:.0f}%" for r in recent],
    })

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )