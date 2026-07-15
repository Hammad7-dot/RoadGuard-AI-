import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration

from ai.webcam_detector import LiveVideoProcessor
from components.sidebar import Sidebar
from utils.styles import load_css

# ---------------------------------------------------
# Page Config
# ---------------------------------------------------

st.set_page_config(
    page_title="Live Monitor",
    page_icon="📹",
    layout="wide"
)

load_css()
Sidebar().render()

st.title("📹 Live Camera Monitor")
st.caption("Real-time road damage tracking from your live camera feed.")

confidence = st.slider(
    "Confidence Threshold",
    min_value=0.10,
    max_value=1.00,
    value=0.50,
    step=0.05
)

# STUN server so the browser can establish a live WebRTC connection
# even when Streamlit is running on a remote/cloud host.
RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)

ctx = webrtc_streamer(
    key="roadguard-live-monitor",
    mode=WebRtcMode.SENDRECV,
    rtc_configuration=RTC_CONFIGURATION,
    video_processor_factory=LiveVideoProcessor,
    media_stream_constraints={"video": True, "audio": False},
    async_processing=True,
)

# Keep the confidence slider in sync with the running processor so
# adjusting it updates detections live, without restarting the stream.
if ctx.video_processor:
    ctx.video_processor.set_confidence(confidence)

status_placeholder = st.empty()

if ctx.state.playing:
    detections = ctx.video_processor.last_detection_count if ctx.video_processor else 0
    unique_defects = ctx.video_processor.unique_defect_count if ctx.video_processor else 0
    fps = ctx.video_processor.last_fps if ctx.video_processor else 0.0

    col1, col2 = st.columns(2)
    col1.metric("Objects Detected (current frame)", detections)
    col2.metric("Unique Defects Tracked (session)", unique_defects)
    st.caption(f"Processing at ~{fps:.1f} FPS")
else:
    status_placeholder.info("Click **Start** above to begin live tracking.")
