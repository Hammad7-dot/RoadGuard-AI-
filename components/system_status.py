import os

import streamlit as st
import psutil

from database.database import get_connection


def _model_status() -> bool:
    """
    Reports whether the YOLO model is actually loaded, rather than a
    static "always green" message. ai.model_loader.load_model() is
    st.cache_resource'd, so calling it here is cheap after the first
    real load elsewhere in the app.
    """
    try:
        from ai.model_loader import load_model
        load_model()
        return True
    except Exception:
        return False


def _database_status() -> bool:
    try:
        conn = get_connection()
        conn.close()
        return True
    except Exception:
        return False


def system_status():

    st.subheader("System Status")

    left, right = st.columns(2)

    with left:

        if _model_status():
            st.success("🟢 YOLO Model Loaded")
        else:
            st.error("🔴 YOLO Model Failed to Load")

        if _database_status():
            st.success("🟢 SQLite Connected")
        else:
            st.error("🔴 SQLite Connection Failed")

        # This line only runs if the Streamlit process is up, so it's
        # trivially true whenever it renders.
        st.success("🟢 Streamlit Running")

    with right:

        st.metric(

            "CPU",

            f"{psutil.cpu_percent()} %"

        )

        st.metric(

            "Memory",

            f"{psutil.virtual_memory().percent} %"

        )

        # os.path.abspath(os.sep) resolves to "/" on Linux/Mac and
        # "C:\\" on Windows, since psutil.disk_usage() needs a real
        # root path for whatever OS this is running on.
        disk_root = os.path.abspath(os.sep)

        st.metric(

            "Disk",

            f"{psutil.disk_usage(disk_root).percent} %"

        )
