import streamlit as st


def about_section():

    st.markdown("## About")

    st.write(
        """
RoadGuard AI helps automate road inspections using
computer vision.

Instead of manually inspecting roads, users can upload
images, analyze videos, or monitor live camera feeds.

The application detects multiple categories of road damage
using a YOLOv8 model and provides analytics and reports.
        """
    )