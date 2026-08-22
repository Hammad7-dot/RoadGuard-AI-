import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration

from ai.webcam_detector import LiveVideoProcessor
from components.confidence_slider import confidence_slider
from utils.page import init_page

# ---------------------------------------------------
# Page Config
# ---------------------------------------------------

init_page("Live Monitor", "📹")

st.title("📹 Live Camera Monitor")
st.caption("Real-time road damage tracking from your live camera feed.")
st.caption(
    "If the camera doesn't start, check that your browser has permission "
    "to use the camera for this site and that no other app is using it."
)

confidence = confidence_slider(key="live_confidence")

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
