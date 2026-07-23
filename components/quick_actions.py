import streamlit as st


def quick_actions():

    st.subheader("Quick Actions")

    c1,c2,c3 = st.columns(3)

    with c1:

        if st.button(
            "📤 Upload Image",
            use_container_width=True
        ):
            st.switch_page("pages/2_Upload_Analysis.py")

    with c2:

        if st.button(
            "📹 Open Live Camera",
            use_container_width=True
        ):
            st.switch_page("pages/4_Live_Monitor.py")

    with c3:

        if st.button(
            "📄 Generate Report",
            use_container_width=True
        ):
            st.switch_page("pages/5_Reports.py")