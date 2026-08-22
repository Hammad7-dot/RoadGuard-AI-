# Decisions Log

Format: Date (best known from git history) — Decision — Why — Status.

| # | Decision | Why | Status |
|---|----------|-----|--------|
| D1 | Use YOLOv8n (`best.pt`) with 4 RDD2022-style classes | Small enough for CPU inference in a free-tier Streamlit deployment | Active |
| D2 | Convert `result.plot()` BGR→RGB immediately inside `detector.py` | A prior bug (`7eb650a`) leaked BGR frames into `st.image`, producing blue-tinted output; centralizing the conversion at the source prevents every caller from having to remember it | Active |
| D3 | SQLite (`database/roadguard.db`) with additive-only migrations via `_migrate_schema()` | Simplicity for a single-tenant demo app; avoids a migration framework dependency | Active |
| D4 | Dashboard stats must be computed from live DB queries, never hardcoded | Repo previously shipped fake/demo numbers (`efc7ab6`); this eroded trust in the tool's core value prop | Active |
| D5 | `packages.txt` pins `libgl1` + `libglib2.0-0t64` | `opencv-python` needs system GL libs on headless Linux hosts (Streamlit Cloud) | Active |
| D6 | `av` pinned `<19`, `>=15.1` | Streamlit-webrtc's `av` dependency previously had no wheel for newer Python, forcing a broken source build (`718bf00`) | Active |
| D7 | No auth/multi-tenancy | Out of scope for current use case (demo/portfolio project); revisit if deployed for real traffic authorities | Open — revisit before any production/public deployment |
| D8 | No LICENSE file yet | Not decided; README explicitly flags this as unresolved | Open |

| D9 | `utils/geotag.py::extract_gps` now reads the GPS sub-IFD via `exif.get_ifd(IFD.GPSInfo)` instead of scanning top-level `exif.items()` | The old code never found real GPS data — `image.getexif().items()` only yields a raw byte-offset int for the GPSInfo tag, not the nested dict, so geotagging silently no-op'd on every real photo. Verified with a synthetic EXIF round-trip test (returned `None` before the fix, correct coordinates after) | Fixed 2026-08-03 |
| D10 | Images with zero detections are now logged via `DetectionRepository.save_no_damage()` (sentinel `damage_type = "No Damage Detected"`, `confidence = NULL`) | Previously a clean image produced no DB row at all, so it was invisible to `get_dashboard_stats()`'s "images analyzed" count, Recent Activity, and the Reports history/CSV — a survey of undamaged roads looked identical to no survey being run. All aggregate queries (`get_dashboard_stats`, `get_damage_distribution`) now explicitly exclude this sentinel from object/confidence/chart counts so it only affects "images analyzed," not detection counts | Fixed 2026-08-03 |

| D11 | `database/database.py::db_connection()` context manager wraps every `database/repository.py` query; `save_video_session` no longer stores placeholder `confidence=1.0`/`x1..y2=0`, storing `NULL` instead | The bare `conn.close()` pattern leaked connections if an exception was raised mid-query; fake placeholder values for video-session rows were a latent trap for any future query on the `detections` table that doesn't explicitly filter `damage_type = 'Video Analysis'` | Fixed 2026-08-06 |
| D12 | `pages/5_Reports.py`'s delete action now requires an explicit confirmation checkbox before the delete button is enabled; `pages/3_Video_Analysis.py` keys its disk-write/DB-write/output-filename on a content hash (not just the uploaded filename), matching the pattern already used in `pages/2_Upload_Analysis.py` | A misclick on "Delete Selected Record" was previously irreversible with no confirmation step; two video uploads with the same filename previously overwrote each other's output file on disk and could double-log a video session on a rerun | Fixed 2026-08-06 |

## Open Questions
- Should `scripts/dedupe_detections.py` become an automatic post-insert
  hook, or stay a manual maintenance script? (Currently manual — no decision
  recorded to change that.)
- Video/webcam pages sample frames rather than process every frame — the
  exact sampling rate is not yet documented as a spec'd constant. Needs a
  named constant + spec entry before it's tuned further.
