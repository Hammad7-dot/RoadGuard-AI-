import pandas as pd
import streamlit as st

from components.sidebar import Sidebar
from database.repository import DetectionRepository

st.set_page_config(
    page_title="Detection History",
    layout="wide"
)

Sidebar().render()

st.title("📄 Detection History")

repo = DetectionRepository()

rows = repo.get_all()

df = pd.DataFrame(rows)

# ---------------------------------
# Search
# ---------------------------------

search = st.text_input(
    "🔍 Search Damage Type"
)

if search and not df.empty:

    df = df[
        df["damage_type"]
        .str.contains(
            search,
            case=False,
            na=False
        )
    ]

# ---------------------------------
# Statistics
# ---------------------------------

st.subheader("📊 Statistics")

# Video session rows store a dummy confidence of 1.0 (there's no
# single per-object confidence for a whole video), so they'd skew
# "Average Confidence" upward if included. Split them out.
image_rows = (
    df[df["damage_type"] != "Video Analysis"]
    if not df.empty
    else df
)
video_rows = (
    df[df["damage_type"] == "Video Analysis"]
    if not df.empty
    else df
)

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Database Records",
    len(df)
)

c2.metric(
    "Unique Damage Types",
    image_rows["damage_type"].nunique() if not image_rows.empty else 0
)

average = (
    image_rows["confidence"].mean() * 100
    if not image_rows.empty
    else 0
)

c3.metric(
    "Average Confidence",
    f"{average:.1f}%"
)

c4.metric(
    "Video Sessions",
    len(video_rows)
)

st.divider()

# ---------------------------------
# Video Sessions
# ---------------------------------

if not video_rows.empty:

    st.subheader("🎥 Video Sessions")

    video_display = video_rows[
        ["id", "filename", "total_frames", "detection_count",
         "unique_defect_count", "processing_time", "created_at"]
    ].rename(columns={
        "detection_count": "total_detections",
    })

    st.dataframe(
        video_display,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

# ---------------------------------
# Detection History
# ---------------------------------

st.subheader("📋 Detection History")

if df.empty:

    st.info("No detections found.")

else:

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    st.download_button(
        "⬇ Export CSV",
        df.to_csv(index=False),
        file_name="road_damage_history.csv",
        mime="text/csv"
    )

st.divider()

st.subheader("🗑 Delete Record")

if not df.empty:

    record_id = st.selectbox(
        "Select Record ID",
        df["id"].tolist()
    )

    if st.button("Delete Selected Record"):

        repo.delete(record_id)

        st.success("Record deleted successfully!")

        st.rerun()