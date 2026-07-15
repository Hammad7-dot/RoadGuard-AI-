import streamlit as st
from datetime import datetime


def welcome_banner():

    st.markdown("""
    <div class="banner">

    <h1>📊 Dashboard</h1>

    <p>
    Welcome to RoadGuard AI.
    Monitor road damage detection,
    analytics and AI performance.
    </p>

    </div>
    """, unsafe_allow_html=True)

    st.caption(
        datetime.now().strftime(
            "%A, %d %B %Y"
        )
    )