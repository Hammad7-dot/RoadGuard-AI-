import streamlit as st


def footer():

    st.divider()

    st.markdown(
        """
<center>

RoadGuard AI • Version 1.0

Made with ❤️ using

Python • Streamlit • YOLOv8

</center>
        """,
        unsafe_allow_html=True
    )