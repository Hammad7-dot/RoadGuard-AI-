import streamlit as st

from utils.constants import VERSION


def footer():

    st.divider()

    st.markdown(
        f"""
        <div class="rg-footer">
            <strong>RoadGuard AI</strong> • Version {VERSION}<br>
            Made with ❤️ using Python • Streamlit • YOLOv8
        </div>
        """,
        unsafe_allow_html=True
    )
