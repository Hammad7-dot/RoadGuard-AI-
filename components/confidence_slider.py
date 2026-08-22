import streamlit as st


def confidence_slider(key: str = None) -> float:
    """
    Shared confidence-threshold slider, previously duplicated verbatim
    across Upload/Video/Live Monitor pages.
    """

    return st.slider(
        "Confidence Threshold",
        min_value=0.10,
        max_value=1.00,
        value=0.50,
        step=0.05,
        key=key,
    )
