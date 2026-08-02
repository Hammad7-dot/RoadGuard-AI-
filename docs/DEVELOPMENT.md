# Development Docs

## Overview

RoadGuard AI is a Streamlit application for road-damage detection using a YOLO model. Users can analyze uploaded images, process videos, monitor live streams, view dashboard metrics, and export inspection reports.

## Main Entry Points

- `app.py`: landing page for the Streamlit application.
- `pages/1_Dashboard.py`: dashboard metrics and distribution charts.
- `pages/2_Upload_Analysis.py`: image upload, YOLO inference, severity scoring, output image saving, and detection persistence.
- `pages/3_Video_Analysis.py`: uploaded video processing and session persistence.
- `pages/4_Live_Monitor.py`: webcam/live monitoring flow.
- `pages/5_Reports.py`: detection history, map display, CSV export, PDF report export, and record deletion.

## Core Modules

- `ai/model_loader.py`: cached YOLO model loading from `utils.constants.MODEL_PATH`.
- `ai/detector.py`: image inference, annotated image generation, detection summaries, and output saving.
- `ai/video_detector.py`: video inference and unique defect counting.
- `ai/webcam_detector.py`: webcam-frame detection support.
- `database/database.py`: SQLite connection, table creation, and schema migration.
- `database/repository.py`: persistence and dashboard/report query helpers.
- `utils/pdf_report.py`: PDF inspection report generation.
- `utils/geotag.py`: EXIF GPS extraction for uploaded images.

## Local Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

The app sets `YOLO_CONFIG_DIR` to `.ultralytics/` inside the project before importing Ultralytics. This avoids user-profile permission errors in restricted environments.

Run the app:

```powershell
streamlit run app.py
```

## Verification

Run syntax compilation:

```powershell
python -m compileall .
```

Run unit tests:

```powershell
python -m unittest discover -s tests
```

Run dependency import check:

```powershell
python -c "from utils.ultralytics_config import configure_ultralytics_settings; configure_ultralytics_settings(); import streamlit, ultralytics, cv2, numpy, pandas, plotly, PIL, psutil, reportlab; print('core dependencies import OK')"
```

Recommended future automated tests:

- Unit-test upload severity and road-condition rules after moving them into a utility module.
- Integration-test `DetectionRepository` against a temporary SQLite database.
- Smoke-test `build_report` with sample stats and rows.

## Data Persistence

The app writes detections to `database/roadguard.db`. The database table is created automatically on import of `database.database`, and migrations add missing columns for video session and geotag support.

Do not commit generated SQLite databases, uploaded media, output media, or local Ultralytics settings.

## Operational Notes

- The bundled model path is controlled by `utils/constants.py`.
- Image analysis writes annotated images to `outputs/`.
- Video analysis writes uploaded videos to `uploads/videos/` and processed videos to `outputs/videos/`.
- Camera and video tests should be done with explicit sample media and recorded in the test notes for the change.
