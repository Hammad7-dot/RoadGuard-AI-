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

if df.empty:

    st.info("No detections found.")

else:

    st.dataframe(

        df,

        use_container_width=True,

        hide_index=True

    )

    st.download_button(

        "⬇ Download CSV",

        df.to_csv(index=False),

        "detections.csv"

    )

# ---------------------------------
# Search
# ---------------------------------

search = st.text_input(
    "🔍 Search Damage Type"
)

if search:

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

c1, c2, c3 = st.columns(3)

c1.metric(
    "Database Records",
    len(df)
)

c2.metric(
    "Unique Damage Types",
    df["damage_type"].nunique() if not df.empty else 0
)

average = (
    df["confidence"].mean() * 100
    if not df.empty
    else 0
)

c3.metric(
    "Average Confidence",
    f"{average:.1f}%"
)

st.divider()

st.subheader("📋 Detection History")

if df.empty:

    st.info("No detections found.")

else:

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

# ---------------------------------
# Export CSV
# ---------------------------------

if not df.empty:

    csv = df.to_csv(index=False)

    st.download_button(

        label="⬇ Export CSV",

        data=csv,

        file_name="road_damage_history.csv",

        mime="text/csv"
    )

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