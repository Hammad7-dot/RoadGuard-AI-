import streamlit as st
from pathlib import Path
from ultralytics import YOLO

from utils.constants import MODEL_PATH

BASE_DIR = Path(__file__).resolve().parent.parent


@st.cache_resource(show_spinner="Loading YOLOv8 model...")
def load_model():
    return YOLO(str(BASE_DIR / MODEL_PATH))
