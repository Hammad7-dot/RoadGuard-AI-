import streamlit as st


def stats_section():

    st.markdown(
        "<h2 style='text-align:center;'>System Overview</h2>",
        unsafe_allow_html=True
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Damage Classes",
        "7"
    )

    c2.metric(
        "YOLO Model",
        "v8"
    )

    c3.metric(
        "Accuracy",
        "96%"
    )

    c4.metric(
        "Inference",
        "18 ms"
    )