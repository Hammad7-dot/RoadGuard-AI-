import streamlit as st

from utils.styles import load_css
from components.hero import hero_section
from components.features import feature_section
from components.stats import stats_section
from components.about import about_section
from components.footer import footer

st.set_page_config(
    page_title="RoadGuard AI",
    page_icon="🛣️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

load_css()

hero_section()

st.divider()

feature_section()

st.divider()

stats_section()

st.divider()

about_section()

footer()