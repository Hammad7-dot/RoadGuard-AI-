import streamlit as st


def quick_actions():

    st.subheader("Quick Actions")

    c1,c2,c3 = st.columns(3)

    with c1:

        st.button(

            "📤 Upload Image",

            use_container_width=True

        )

    with c2:

        st.button(

            "📹 Open Live Camera",

            use_container_width=True

        )

    with c3:

        st.button(

            "📄 Generate Report",

            use_container_width=True

        )