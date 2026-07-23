import streamlit as st
import pandas as pd
import plotly.express as px

from database.repository import DetectionRepository


def damage_chart():

    st.subheader("Road Damage Statistics")

    distribution = DetectionRepository().get_damage_distribution()

    if not distribution:
        st.info("No detections yet — run some analyses to populate this chart.")
        return

    df = pd.DataFrame({
        "Damage": list(distribution.keys()),
        "Count": list(distribution.values())
    })

    left,right = st.columns(2)

    with left:

        fig = px.bar(

            df,

            x="Damage",

            y="Count",

            title="Damage Distribution"

        )

        st.plotly_chart(

            fig,

            use_container_width=True

        )

    with right:

        fig = px.pie(

            df,

            names="Damage",

            values="Count",

            hole=.45,

            title="Damage Percentage"

        )

        st.plotly_chart(

            fig,

            use_container_width=True

        )