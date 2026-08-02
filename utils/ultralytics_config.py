import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


def configure_ultralytics_settings() -> None:
    os.environ.setdefault(
        "YOLO_CONFIG_DIR",
        str(BASE_DIR / ".ultralytics")
    )
