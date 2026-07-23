import streamlit as st


def feature_section():

    st.markdown(
        "<h2 style='text-align:center;'>✨ Features</h2>",
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.info("""
### 🎯 AI Detection

Detect:

- Potholes
- Longitudinal Cracks
- Transverse Cracks
- Alligator Cracks
""")

    with c2:
        st.success("""
### 📹 Live Monitoring

- Webcam
- Video
- Real-time Detection
- Instant Alerts
""")

    with c3:
        st.warning("""
### 📊 Analytics

- Reports
- Charts
- Detection History
- Statistics
""")