# Handbrake Blocked

This file records conditions that should block or pause a RoadGuard AI change before it is merged, released, or demoed.

## Current Test Status

Date: 2026-08-02

Automated checks run:

- `python -m compileall .` passed.
- `python -m unittest discover -s tests` passed.
- Dependency import smoke test passed.
- `utils.ultralytics_config.configure_ultralytics_settings()` now sets `YOLO_CONFIG_DIR` to `.ultralytics` inside the project before repository code imports Ultralytics.

Resolved environment blocker:

- Importing `ultralytics` without `YOLO_CONFIG_DIR` failed because the sandbox could not read `C:\Users\dell\AppData\Roaming\Ultralytics\settings.json`.

Fix: project-local Ultralytics settings are configured automatically by app model loading and training entry points.

## Merge Blockers

- Syntax compilation fails.
- Required dependencies cannot be imported in the target environment.
- The YOLO model file is missing or cannot be loaded.
- Upload, video, live monitor, dashboard, or report pages crash on startup.
- Database migration fails or drops existing detection history.
- Duplicate detections are written from normal Streamlit reruns.
- Report exports contain misleading totals, confidence values, or geolocation data.
- Uploaded media, generated outputs, SQLite databases, caches, or local settings are staged for commit.

## Release Blockers

- No manual verification has been recorded for changed Streamlit pages.
- No sample image or video has been used to confirm model output after inference changes.
- Camera behavior is changed without checking permission-denied and unavailable-camera states.
- Geotag handling is changed without checking missing EXIF, invalid coordinates, and manually entered coordinates.
- PDF or CSV export changes are not opened and inspected.

## Handbrake Procedure

1. Stop the release or merge.
2. Write the blocker under this file with date, command, failure, and suspected owner.
3. Create or update the spec with the missing acceptance criteria.
4. Fix the issue in the smallest safe change.
5. Re-run the relevant checks and record the result.
