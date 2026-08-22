# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

RoadGuard AI is a Streamlit app that detects road surface damage (longitudinal/transverse/alligator cracks,
potholes) in uploaded images, video, and live webcam feed using a YOLOv8n model, logs detections to SQLite,
and presents them through a dashboard with PDF/CSV export.

This repo practices spec-driven development. Read `docs/SPEC.md`, `docs/RULES.md`, and `docs/DECISIONS.md`
before non-trivial changes — they are the enforced source of truth, not just background reading.

## Commands

```bash
pip install -r requirements.txt          # install deps
streamlit run app.py                     # run the app (localhost:8501)
python -m compileall .                   # required before any change (RULES.md R17)
python -m unittest discover tests        # run all tests
python -m unittest tests.test_detector_metrics.RoadDamageDetectorMetricsTest.test_average_confidence_rounds_to_three_decimals  # single test
```

In sandboxed/restricted environments, `ultralytics` needs `YOLO_CONFIG_DIR` pointed at a project-local
writable path *before* it's imported, or model loading/training/tests will fail to start. See
`utils/ultralytics_config.py` (RULES.md R16) — import it first in any new entry point that touches
`ultralytics`.

## Architecture

Data flow (see `docs/SPEC.md` §2 for the full diagram):

```
Input (image / video / webcam)
  → ai/detector.py (RoadDamageDetector), via ai/model_loader.py → ai/models/best.pt (YOLOv8n, 4-class)
  → annotated RGB frame + detections list
      → database/repository.py → database/database.py (SQLite: roadguard.db)
      → components/* (dashboard cards, charts, summaries)
          → pages/*.py (Streamlit multipage UI)
              → utils/pdf_report.py (PDF export)
```

- **`app.py`** is the landing/marketing page only. Actual functionality lives in `pages/1..5_*.py`.
  Keep pages thin (layout + wiring); reusable logic belongs in `ai/`, `database/`, `components/`, or `utils/`
  (RULES.md R12).
- **Color space invariant**: detector output must be RGB by the time it reaches `st.image` or is saved —
  conversion happens once, at the boundary, inside `ai/detector.py`. A historical bug (commit `7eb650a`)
  leaked BGR frames into the UI; don't do ad hoc BGR/RGB conversion in UI code (RULES.md R2).
  Any function touching a frame as a numpy array must document RGB vs BGR in its docstring.
- **Single source of truth**: model path and damage classes live only in `utils/constants.py`
  (`MODEL_PATH`, `DAMAGE_CLASSES`); DB path/schema live only in `database/database.py`. Never hardcode a
  second copy elsewhere (RULES.md R6). `DAMAGE_CLASSES` must always equal `model.names` for whatever
  `best.pt` is loaded — verify manually whenever the weights file changes (RULES.md R5).
- **Database**: single `detections` table in SQLite (`database/roadguard.db`). Schema changes go through
  `database/database.py::_migrate_schema()` and must be additive-only (`ALTER TABLE ADD COLUMN`) — never
  drop or rename a column in place (RULES.md R4). All queries use `?` placeholders, never string-interpolated
  input (R13), and every `get_connection()` is paired with `conn.close()` on every path including errors (R14).
- **No fake data**: every number/chart shown in `pages/*.py` or `components/*.py` must come from a live
  `database/repository.py` call — this repo previously shipped hardcoded dashboard stats (`efc7ab6`) and
  regressing on that is a hard block (RULES.md R3, `docs/handbrake-blocked.md`).
- **Severity scoring** (`pages/2_Upload_Analysis.py::_severity`): `score = confidence*0.6 + min(area_ratio*10, 1.0)*0.4`,
  thresholds `>=0.65` High, `>=0.40` Medium, else Low. Changing these thresholds is a behavior change requiring
  a `docs/SPEC.md` update.
- **Geolocation**: only attach lat/long when explicitly read from EXIF or user-entered (`utils/geotag.py`,
  `use_location` checkbox in `pages/2_Upload_Analysis.py`). Never infer or guess coordinates (RULES.md R15).
- **Dependency pins** in `requirements.txt` — `av`, `ultralytics`, `opencv-python-headless` — resolve real
  past deployment breakages (`docs/DECISIONS.md` D6). Don't loosen them without testing a fresh install on a
  clean environment. `packages.txt` (`libgl1`, `libglib2.0-0t64`) is required for `opencv-python` on headless
  Linux (Streamlit Cloud) — don't remove.

## Hard blocks

`docs/handbrake-blocked.md` lists actions that are blocked regardless of who asks or how urgently — treat it
as a hard stop, never something to lift yourself. Notably: force-pushing `main`, destructive/dropping schema
changes, deleting or overwriting a deployed `roadguard.db`, committing secrets, swapping `ai/models/best.pt`
without verifying `model.names` still matches `DAMAGE_CLASSES`, loosening the `av`/`ultralytics`/
`opencv-python-headless` pins without a clean-environment test, and reintroducing hardcoded/mocked stats.

## Workflow

Per `docs/SPEC.md` §6: update the relevant `docs/SPEC.md` section before behavior changes, add a
`docs/DECISIONS.md` entry for architectural changes (schema, model, severity formula, invariants), then write
code, then record what was verified in `docs/TEST_REPORT.md`. Any change touching uploads, video, live camera,
reports, maps, or dashboard behavior needs a manual click-through of the affected page(s) — `compileall`
passing is necessary but not sufficient (RULES.md R18).
