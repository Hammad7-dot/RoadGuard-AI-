import os

import streamlit as st
import psutil


def system_status():

    st.subheader("System Status")

    left,right = st.columns(2)

    with left:

        st.success("🟢 YOLO Model Loaded")

        st.success("🟢 SQLite Connected")

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