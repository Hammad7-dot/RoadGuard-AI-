import streamlit as st


def dashboard_cards():

    st.subheader("Overview")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Images",
        "124"
    )

    c2.metric(
        "Videos",
        "28"
    )

    c3.metric(
        "Detections",
        "536"
    )

    c4.metric(
        "Accuracy",
        "96.8%"
    )