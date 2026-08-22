import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


def configure_ultralytics_settings() -> None:
    os.environ.setdefault(
        "YOLO_CONFIG_DIR",
        str(BASE_DIR / ".ultralytics")
    )
    # Works around "OMP: Error #15" on Windows when torch/ultralytics and
    # numpy/MKL each ship their own OpenMP runtime DLL — see Intel's own
    # workaround referenced in that error message.
    os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
