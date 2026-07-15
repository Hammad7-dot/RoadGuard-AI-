import streamlit as st

from database.repository import DetectionRepository


class Sidebar:
    """
    Shared sidebar rendered on every page: branding + quick stats.
    """

    def render(self):

        with st.sidebar:

            st.markdown(
                """
                <div style="text-align:center; padding: 10px 0 15px 0;">
                    <div style="font-size:34px;">🛣️</div>
                    <div style="font-size:22px; font-weight:800; color:white;">
                        Road<span style="color:#8B5CF6;">Guard</span> AI
                    </div>
                    <div style="font-size:13px; color:#94A3B8; margin-top:4px;">
                        AI-Powered Road Damage Detection
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.divider()

            st.caption("QUICK STATS")

            try:
                total = DetectionRepository().total_detections()
            except Exception:
                total = 0

            st.metric("Detections Logged", total)

            st.divider()

            st.caption("RoadGuard AI • v1.0.0")
