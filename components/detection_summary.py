import streamlit as st
import pandas as pd


def detection_summary(summary: dict):

    st.subheader("📊 Detection Summary")

    if not summary:

        st.info("No damages detected.")
        return

    df = pd.DataFrame({

        "Damage Type": list(summary.keys()),

        "Count": list(summary.values())

    })

    c1, c2 = st.columns(2)

    with c1:

        st.dataframe(
            df,
            hide_index=True,
            use_container_width=True
        )

    with c2:

        st.bar_chart(
            df.set_index("Damage Type")
        )