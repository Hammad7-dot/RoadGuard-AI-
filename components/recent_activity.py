import streamlit as st
import pandas as pd


def recent_activity():

    st.subheader("Recent Activity")

    df = pd.DataFrame({

        "Time":[

            "10:20",

            "10:18",

            "10:15",

            "10:10"

        ],

        "Damage":[

            "Pothole",

            "Patch",

            "Longitudinal Crack",

            "Manhole"

        ],

        "Confidence":[

            "98%",

            "95%",

            "92%",

            "97%"

        ]

    })

    st.dataframe(

        df,

        use_container_width=True,

        hide_index=True
    )
    