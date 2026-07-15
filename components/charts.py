import streamlit as st
import pandas as pd
import plotly.express as px


def damage_chart():

    st.subheader("Road Damage Statistics")

    df = pd.DataFrame({

        "Damage":[

            "Pothole",

            "Longitudinal",

            "Transverse",

            "Patch",

            "Manhole",

            "Road Marking"

        ],

        "Count":[

            32,

            18,

            12,

            9,

            6,

            4

        ]

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