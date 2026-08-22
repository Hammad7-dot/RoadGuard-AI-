import pandas as pd
import streamlit as st

from database.repository import DetectionRepository
from utils.pdf_report import build_report
from utils.page import init_page

init_page("Detection History", "📄")

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

geotagged = repo.get_geotagged()

with st.spinner("Building PDF report..."):
    pdf_bytes = build_report(
        stats={
            "images_analyzed": len(image_rows["filename"].unique()) if not image_rows.empty else 0,
            "videos_analyzed": len(video_rows),
            "total_detections": len(df),
            "avg_confidence": (average / 100) if not image_rows.empty else None,
        },
        distribution=(
            image_rows["damage_type"].value_counts().to_dict()
            if not image_rows.empty else {}
        ),
        rows=rows,
        geotagged=geotagged,
    )

st.download_button(
    "📄 Export PDF Inspection Report",
    pdf_bytes,
    file_name="roadguard_inspection_report.pdf",
    mime="application/pdf",
)

st.divider()

# ---------------------------------
# Map of geotagged detections
# ---------------------------------

if geotagged:

    st.subheader("🗺️ Detection Map")
    st.caption("Detections with GPS coordinates attached at upload time.")

    map_df = pd.DataFrame(geotagged)[["latitude", "longitude"]]
    st.map(map_df, latitude="latitude", longitude="longitude")

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

    confirm_delete = st.checkbox(
        f"I confirm I want to permanently delete record #{record_id}"
    )

    if st.button("Delete Selected Record", disabled=not confirm_delete):

        repo.delete(record_id)

        st.success("Record deleted successfully!")

        st.rerun()