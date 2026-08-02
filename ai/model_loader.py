from pathlib import Path

import streamlit as st

from utils.ultralytics_config import configure_ultralytics_settings

BASE_DIR = Path(__file__).resolve().parent.parent

configure_ultralytics_settings()

from ultralytics import YOLO

from utils.constants import MODEL_PATH


@st.cache_resource(show_spinner="Loading YOLOv8 model...")
def load_model():
    return YOLO(str(BASE_DIR / MODEL_PATH))
