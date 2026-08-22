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

## Pass 3 — 2026-08-06: bug-fix + frontend redesign pass

Ran three parallel Explore passes over `ai/`+`database/`, `pages/*.py`, and
the CSS/components layer to find real bugs and UI issues before making
changes (see `docs/DECISIONS.md` D11/D12 for the architectural entries).

**Bugs fixed:**

| Area | Bug | Fix |
|---|---|---|
| `ai/video_detector.py` | `cv2.VideoCapture`/`VideoWriter` failures were silent (no `isOpened()` check) | Raises a new `VideoDecodeError` with a clear message; `pages/3_Video_Analysis.py` catches it and shows `st.error` |
| `ai/webcam_detector.py::LiveVideoProcessor.recv` | An inference exception crashed the WebRTC background thread | Wrapped in `try/except`, falls back to the raw frame |
| `ai/detector.py::save_output` | Wrote to a relative `Path("outputs")`, a second source of truth vs. `utils/config.py::OUTPUT_DIR` | Now uses `OUTPUT_DIR` directly |
| `database/database.py`, `database/repository.py` | No `try/finally` around connections — an exception mid-query leaked the connection | Added `db_connection()` context manager; every repository method now uses it |
| `database/repository.py::save_video_session` | Wrote placeholder `confidence=1.0`, `x1..y2=0` instead of `NULL` for video-session rows | Now omits those columns (stored as `NULL`) |
| `pages/5_Reports.py` | Missing `load_css()` call (every other page has it) | Now uses the shared `utils/page.py::init_page` helper |
| `pages/5_Reports.py` | Delete button had no confirmation step before an irreversible DB delete | Added a required confirmation checkbox before the delete button is enabled |
| `pages/3_Video_Analysis.py` | Video bytes rewritten to disk on every rerun; `output_path` reused `video.name`, so two different uploads with the same filename overwrote each other's output; no guard against duplicate DB rows from re-clicking "Start Detection" | Keyed on content hash + confidence via `st.session_state`, mirroring the existing pattern in `pages/2_Upload_Analysis.py` |
| `pages/2_Upload_Analysis.py` | Cache/widget keys derived from filename+size only — two different files with the same name and size collided | Keyed on an MD5 content hash instead |
| `pages/4_Live_Monitor.py` | No user-facing guidance for camera-unavailable/permission-denied states | Added a caption explaining what to check if the camera doesn't start |

**Frontend redesign:** rewrote `assets/style.css` with CSS custom
properties (design tokens), removed the duplicated/dead rule blocks,
added responsive breakpoints for headings/columns, replaced the
`st.info/success/warning`-as-card anti-pattern in `components/features.py`
with real `.rg-card` markup, dropped the deprecated `<center>` tag in
`components/footer.py`, made `components/system_status.py`'s health
checks real (actually calls `load_model()` / opens a DB connection
instead of always showing green), and centralized the version string
(`utils/constants.py::VERSION`) instead of two separate hardcoded
literals. Extracted shared `utils/page.py::init_page()` (replacing the
`set_page_config` + `load_css` + `Sidebar().render()` boilerplate
copy-pasted on every page) and `components/confidence_slider.py`
(replacing three duplicated slider definitions).

**Verification performed:**

| Check | Result |
|---|---|
| `python -m compileall .` | ✅ 0 errors |
| `python -m unittest discover tests` | ✅ 15/15 passed (4 existing + 5 new `test_repository.py` + 6 new `test_geotag.py`) |
| `streamlit run app.py` headless boot, `curl` landing page | ✅ HTTP 200, no exceptions in server log |
| `curl` all 5 `pages/*.py` routes while server running | ✅ HTTP 200 on Dashboard, Upload_Analysis, Video_Analysis, Live_Monitor, Reports; no exceptions in server log |

**Not verified in this pass** (no browser available in this environment):
actual visual rendering of the redesigned CSS/cards, the upload →
detection → save round-trip through the real UI, live webcam permission
flows, and PDF/CSV export content. Recommended before shipping: open the
app in a real browser, upload a sample image and a sample video, and open
the exported PDF.

## Pass 4 — 2026-08-15: real-browser verification (closes out Pass 3's shipping checklist)

Ran the checks Pass 3 flagged as outstanding: a clean local install and a real
click-through in an actual browser, rather than headless `curl`.

| Check | Result |
|---|---|
| Clean venv + `pip install -r requirements.txt` (`ultralytics`, `opencv-python-headless`, `streamlit-webrtc`, `av`, etc.) | ✅ succeeded, no dependency conflicts |
| `streamlit run app.py`; confirmed `app.py` is landing-page-only per architecture | ✅ launched at `localhost:8501` |
| All 5 pages (Dashboard, Upload Analysis, Video Analysis, Live Monitor, Reports) clicked through in a real browser | ✅ no errors; stats confirmed live/DB-backed, not hardcoded (R3) |
| Uploaded a real (non-synthetic) road-damage photo | ✅ bounding-box colors correct (RGB, no BGR leak — R2); new row written to `roadguard.db` (Database Records 67→68) |
| PDF export (`build_report()`) | ✅ produced a valid, non-blank 6.8KB `%PDF-1.4` file |
| `python -m compileall .` | ✅ 0 errors (R17 gate) |
| Live Monitor / webcam page | ⏭️ Not tested — no physical webcam available in this environment |

**Note:** the test photo's only detection was below the 0.50 confidence
threshold (confidence 0.10), so it correctly logged as "No Damage Detected"
rather than a persisted bounding box — expected threshold behavior, not a
bug. Use a higher-confidence sample image to verify a full bounding-box row
end-to-end.

**Still not verified:** the Live Monitor/webcam permission flow (needs a
real camera), and a persisted detection with actual bounding-box
coordinates (needs a higher-confidence sample image). Nothing from this
pass has been committed yet.
