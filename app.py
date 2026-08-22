from utils.page import init_page
from components.hero import hero_section
from components.features import feature_section
from components.stats import stats_section
from components.about import about_section
from components.footer import footer

import streamlit as st

init_page(
    "RoadGuard AI",
    "🛣️",
    show_sidebar=False,
    sidebar_state="collapsed",
)

hero_section()

st.divider()

feature_section()

st.divider()

stats_section()

st.divider()

about_section()

footer()