import streamlit as st


def hero_section():

    left, right = st.columns([1.2, 1])

    with left:

        st.markdown(
            """
            <div class="hero-title">

            <span class="purple">RoadGuard AI</span>

            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <div class="hero-subtitle">

            AI-powered road damage detection using YOLOv8.

            Detect potholes, cracks and road defects from
            images, videos and live cameras.

            </div>
            """,
            unsafe_allow_html=True
        )

        col1, col2 = st.columns(2)

        with col1:

            st.button(
                "🚀 Get Started",
                use_container_width=True,
                type="primary"
            )

        with col2:

            st.button(
                "📄 Documentation",
                use_container_width=True
            )

    with right:

        st.image(
            "assets/hero.jpg",
            use_container_width=True
        )