# RoadGuard AI — Specification (Spec-Driven Development)

Status: Living document. Every feature change starts here, not in code.
Test basis: repo cloned and verified 2026-08-02 — see `docs/TEST_REPORT.md`.

## 1. Purpose

RoadGuard AI detects road surface damage (cracks, potholes) in images, video,
and live webcam feed using a YOLOv8 model, logs detections to SQLite, and
presents them through a Streamlit dashboard with PDF export.

## 2. System Overview

```
Input (image / video / webcam)
        │
        ▼
ai/detector.py (RoadDamageDetector)
        │  uses ai/model_loader.py → ai/models/best.pt (YOLOv8n, 4-class)
        ▼
Annotated frame + detections list
        │
        ├──► database/repository.py → database/database.py (SQLite: roadguard.db)
        │
        └──► components/* (dashboard cards, charts, summaries)
                    │
                    ▼
              pages/*.py (Streamlit multipage UI)
                    │
                    ▼
              utils/pdf_report.py (ReportLab export)
```

## 3. Functional Specs (by module)

### 3.1 Detection Engine — `ai/detector.py`
- **Input:** `PIL.Image.Image`, optional `confidence` (default `0.50`).
- **Output:** `(annotated_image: np.ndarray RGB, detections: List[Dict])`.
- **Detection dict shape:**
  ```json
  {"Class": str, "Confidence": float, "Bounding Box": {"x1":int,"y1":int,"x2":int,"y2":int}}
  ```
- **Invariant:** `annotated_image` MUST be RGB before it reaches `st.image` or
  `save_output` (fixed historically — see commit `7eb650a`, BGR/RGB bug).
  Any new code path that touches frames must preserve this invariant.
- Helper statics: `detection_summary`, `average_confidence`, `total_objects`
  operate only on the detections list — no I/O, easy to unit test.

### 3.2 Model Loading — `ai/model_loader.py`
- Loads `ai/models/best.pt` via `ultralytics.YOLO`, cached with
  `st.cache_resource` (loaded once per server process).
- **Spec rule:** model path is sourced from `utils/constants.py::MODEL_PATH`
  only. Never hardcode a path a second time.

### 3.3 Damage Taxonomy — `utils/constants.py`
- Exactly 4 classes (RDD2022-derived, matches the deployed model —
  see commit `54b1fec`): Longitudinal Crack, Transverse Crack,
  Alligator Crack, Pothole.
- **Spec rule:** `DAMAGE_CLASSES` must always equal `model.names` from the
  loaded weights. If the model is retrained with a different class set,
  this constant MUST be updated in the same PR — drift here previously
  caused a "misleading feature claims" bug (`efc7ab6`).

### 3.4 Severity Scoring — `pages/2_Upload_Analysis.py::_severity`
- `score = confidence*0.6 + min(area_ratio*10, 1.0)*0.4`
- Thresholds: `>=0.65` High, `>=0.40` Medium, else Low.
- Rationale (from code comments): confidence alone doesn't capture how
  serious a defect looks; box-area-relative-to-frame is a cheap severity proxy.
- **Spec rule:** any change to these thresholds is a behavior change and
  requires a spec update + changelog entry, since it changes what users see
  as "High severity."

### 3.5 Persistence — `database/database.py`, `database/repository.py`
- SQLite file at `database/roadguard.db`, single table `detections`.
- Schema evolves via `_migrate_schema()` (additive `ALTER TABLE`, no drops).
- **Spec rule:** schema changes are additive-only in this table. Destructive
  migrations (column drops/renames) require a new migration function and a
  documented upgrade path in `docs/DECISIONS.md`.
- Known past bug (fixed, `eb2933b`): `sqlite3.Row` vs pandas column-name
  mismatch. Any code converting `Row` objects to DataFrames must explicitly
  name columns rather than relying on positional access.

### 3.6 UI — `app.py`, `pages/*.py`, `components/*`
- `app.py`: landing/marketing page only (hero, features, stats, about).
- `pages/1_Dashboard.py`: aggregate stats from real DB queries (not mocked —
  fixed in `7eb650a`/`efc7ab6`, which replaced fake dashboard numbers).
- `pages/2_Upload_Analysis.py`: image upload → detection → severity → save.
- `pages/3_Video_Analysis.py`: video file → frame-sampled detection.
- `pages/4_Live_Monitor.py`: webcam via `streamlit-webrtc`.
- `pages/5_Reports.py`: history + PDF export via `utils/pdf_report.py`.
- **Spec rule:** every dashboard number displayed must trace to a live DB
  query. No hardcoded/demo stats are permitted (this was a real regression
  before; don't reintroduce it).

### 3.7 Geotagging — `utils/geotag.py`
- Extracts GPS EXIF from uploaded images when present; optional, must not
  raise if EXIF/GPS tags are absent.

### 3.8 Deduplication — `scripts/dedupe_detections.py`
- Offline/manual script to collapse duplicate detection rows. Not run
  automatically by the app. Spec rule: keep it idempotent — running it twice
  must not change the result of running it once.

## 4. Non-Functional Requirements
- Python 3.8+ (repo claims); model loading via `ultralytics` requires enough
  RAM for a YOLOv8n forward pass (~small, CPU-friendly).
- `packages.txt` (`libgl1`, `libglib2.0-0t64`) required for `opencv-python`
  on headless Linux (e.g. Streamlit Community Cloud) — do not remove.
- No secrets, API keys, or PII beyond image EXIF should be committed.

## 5. Out of Scope (explicitly, per README)
- No license currently declared — treat repo as "all rights reserved" until
  a LICENSE file is added.
- No authentication/authorization layer exists — do not assume multi-user
  isolation; `roadguard.db` is single-tenant.

## 6. How to Propose a Change (SDD workflow)
1. Write/update the relevant section of this `SPEC.md` first.
2. Add or update an entry in `docs/DECISIONS.md` if the change is
   architectural (schema, model, severity formula, invariants).
3. Only then write code.
4. Update `docs/TEST_REPORT.md` with what you verified.
5. PR description must link back to the spec section changed.

See `docs/RULES.md` for enforceable engineering rules and
`docs/handbrake-blocked.md` for hard stop conditions.
