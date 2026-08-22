import streamlit as st


def _card(icon: str, title: str, items: list):
    items_html = "".join(f"<li>{item}</li>" for item in items)
    st.markdown(
        f"""
        <div class="rg-card">
            <div class="rg-card-icon">{icon}</div>
            <div class="rg-card-title">{title}</div>
            <ul class="rg-card-list">{items_html}</ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


def feature_section():

    st.markdown(
        "<h2 style='text-align:center;'>✨ Features</h2>",
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        _card(
            "🎯",
            "AI Detection",
            [
                "Potholes",
                "Longitudinal Cracks",
                "Transverse Cracks",
                "Alligator Cracks",
            ],
        )

    with c2:
        _card(
            "📹",
            "Live Monitoring",
            [
                "Webcam",
                "Video",
                "Real-time Detection",
                "Instant Alerts",
            ],
        )

    with c3:
        _card(
            "📊",
            "Analytics",
            [
                "Reports",
                "Charts",
                "Detection History",
                "Statistics",
            ],
        )
