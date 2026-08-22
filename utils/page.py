import streamlit as st

from utils.styles import load_css
from components.sidebar import Sidebar


def init_page(title: str, icon: str, layout: str = "wide", show_sidebar: bool = True, sidebar_state: str = None):
    """
    Shared page bootstrap: set_page_config + load_css + sidebar render.
    Every page/app.py previously copy-pasted this same three-call
    sequence (and Reports had silently dropped the load_css() call).
    """

    kwargs = dict(page_title=title, page_icon=icon, layout=layout)
    if sidebar_state:
        kwargs["initial_sidebar_state"] = sidebar_state

    st.set_page_config(**kwargs)

    load_css()

    if show_sidebar:
        Sidebar().render()
