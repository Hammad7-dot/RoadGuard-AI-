# Test Report — RoadGuard AI

Date: 2026-08-02
Scope: Clone + static/runtime smoke test of `main` (commit `762aab6`).

## What was tested

| Check | Result |
|---|---|
| Clone repo, inspect structure | ✅ 33 Python files across `ai/`, `components/`, `database/`, `pages/`, `scripts/`, `training/`, `utils/`, plus `app.py` |
| `python -m py_compile` on every `.py` file | ✅ 0 syntax errors |
| `ast.parse` on every `.py` file | ✅ 0 parse errors |
| `ai/models/best.pt` present | ✅ present, ~6.2 MB (consistent with YOLOv8n) |
| `database/database.py` — `create_tables()` + `_migrate_schema()` run live | ✅ ran without error, created `detections` table with all documented columns |
| `requirements.txt` / `packages.txt` reviewed for known-fragile pins | ✅ `av`, `ultralytics`, `opencv-python-headless` all pinned per D6 |
| Full `streamlit run app.py` end-to-end launch | ❌ Not run — needs `ultralytics`, `opencv-python-headless`, `streamlit-webrtc`, `av` installed (heavy, GPU/codec-adjacent deps not exercised in this environment) |
| YOLOv8 inference on a sample image | ❌ Not run — same reason |
| Webcam/live monitor page (`pages/4_Live_Monitor.py`) | ❌ Not run — requires a real webcam/WebRTC session |
| PDF report generation (`utils/pdf_report.py`) | ❌ Not run |

## Interpretation

The codebase is structurally sound: everything parses, imports are
consistent with the module layout, and the lightweight parts (SQLite layer)
run correctly against live SQLite. The heavier ML/video pipeline
(YOLO inference, webcam, PDF) was **not** functionally exercised in this
pass — that requires installing `ultralytics` + `opencv-python-headless` +
`streamlit-webrtc` + `av` and either a sample image/video or a webcam, which
wasn't done here due to environment constraints.

## Pass 2 — 2026-08-03: full install + bug hunt

Installed the full dependency set (`ultralytics`, `opencv-python-headless`,
`streamlit-webrtc`, `av`, `reportlab`, `plotly`, `psutil`) and exercised the
code paths that Pass 1 couldn't reach.

| Check | Result |
|---|---|
| `ai/detector.py::RoadDamageDetector.predict()` against the real `best.pt` weights | ✅ model loads, `class_names` = 4 RDD2022 classes matching `DAMAGE_CLASSES` order, inference runs, output is correctly RGB |
| Import every module in `components/`, `database/`, `utils/` | ✅ all clean |
| `database/repository.py` live round-trip (image detection, video session, dashboard stats, distribution, geotagged) | ✅ correct after fixes (see below) |
| `utils/geotag.py::extract_gps` against a real synthetic EXIF GPS block | 🐛 **Bug found and fixed** — see D9. Was silently returning `None` for every real photo. |
| Zero-detection ("clean") image upload flow | 🐛 **Bug found and fixed** — see D10. Clean images were never logged to the DB at all. |
| `components/recent_activity.py` confidence formatting after D10's `NULL`-confidence rows exist | 🐛 **Bug found and fixed** — would have raised `TypeError` on `None * 100`; now guarded with `if r["confidence"] is not None else "-"` |
| `utils/pdf_report.py` confidence formatting with `NULL` confidence | ✅ already guarded (`if conf is not None else "N/A"`), no change needed |
| Re-ran `py_compile` on all files after fixes | ✅ 0 errors |

Not yet run: full `streamlit run app.py` browser click-through, live webcam
session, real (non-synthetic) uploaded photo through the UI. Recommended
before shipping to a real user.

## Recommended next verification pass
1. `pip install -r requirements.txt` in a clean venv (matches README).
2. `streamlit run app.py`, click through all 5 pages.
3. Upload one real road-damage image → confirm bounding boxes render in
   correct color (RGB, not BGR — R2) and detections get persisted to
   `roadguard.db`.
4. Run `pages/5_Reports.py` → export PDF → open and check content.
5. Re-run `python -m py_compile` after any future change as a pre-merge gate
   (RULES.md R10).
