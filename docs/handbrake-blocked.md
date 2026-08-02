# 🛑 Handbrake — Blocked Actions

This file lists actions that are **blocked by default** in this repository.
"Blocked" means: do not perform this action — not even if asked directly,
not even under time pressure, not even by editing around this file — until
a human maintainer explicitly updates this document to lift the block.

If you are an AI agent or contributor working on this repo, treat this file
as a hard stop, not a checklist to talk yourself past.

## Blocked

- **Force-pushing to `main`.** Any rewrite of `main` history is blocked.
  Use a branch + PR, always.
- **Deleting or rewriting `database/roadguard.db` in a shared/deployed
  environment.** Local dev DBs can be reset; a deployed DB holding real
  detection history cannot be dropped, truncated, or overwritten.
- **Removing `_migrate_schema()`'s additive-only guarantee** (i.e. adding a
  `DROP COLUMN` / destructive `ALTER TABLE`) without a written migration
  plan reviewed in `docs/DECISIONS.md` first.
- **Committing secrets, API keys, or `.env` files.**
- **Replacing `ai/models/best.pt` with an unverified model** — i.e. swapping
  the weights file without confirming `model.names` still matches
  `utils/constants.py::DAMAGE_CLASSES` (see RULES.md R5). A silent mismatch
  makes every downstream label wrong.
- **Loosening `av`, `ultralytics`, or `opencv-python-headless` version pins
  in `requirements.txt`** without a clean-environment install test. These
  pins exist because of a real, previously-shipped deployment breakage
  (see `docs/DECISIONS.md` D6).
- **Reintroducing hardcoded/mocked stats into any Streamlit page.** This
  was shipped once (`efc7ab6` fixed it) and is explicitly not allowed again
  (RULES.md R3).
- **Running `scripts/dedupe_detections.py` (or any destructive data script)
  directly against a production/deployed database without a backup first.**
- **Adding a license, changing the license, or adding third-party model
  weights/datasets of unclear provenance** without the repo owner's
  explicit sign-off — this is a legal/IP decision, not an engineering one.
- **Auto-merging any PR that skips the R10 test-before-merge step.**

## Merge Blockers
A PR must not be merged if any of these are true:
- Syntax compilation fails (`python -m compileall .`).
- Required dependencies cannot be imported in the target environment.
- The YOLO model file is missing or cannot be loaded.
- Upload, video, live monitor, dashboard, or report pages crash on startup.
- Database migration fails or drops existing detection history.
- Duplicate detections are written from normal Streamlit reruns (see the
  session-state caching pattern in `pages/2_Upload_Analysis.py`).
- Report exports (PDF/CSV) contain misleading totals, confidence values, or
  geolocation data.
- Uploaded media, generated outputs, SQLite databases, caches, or local
  settings are staged for commit.

## Release Blockers
Do not ship/demo a change if any of these haven't been done:
- No manual verification recorded for changed Streamlit pages.
- No sample image or video used to confirm model output after an
  inference-affecting change.
- Camera behavior changed without checking permission-denied and
  unavailable-camera states.
- Geotag handling changed without checking missing EXIF, invalid
  coordinates, and manually entered coordinates (see D9 — this exact area
  had a real, previously-shipped bug).
- PDF or CSV export changes made without opening and inspecting the output.

## Handbrake Procedure
If a merge/release blocker is hit:
1. Stop the release or merge.
2. Write the blocker into this file (or `docs/DECISIONS.md` if
   architectural) with date, command run, failure observed, and suspected
   owner.
3. Create or update the spec (`docs/SPEC.md`) with the missing acceptance
   criteria.
4. Fix the issue in the smallest safe change.
5. Re-run the relevant checks and record the result in
   `docs/TEST_REPORT.md`.

## Environment Notes (resolved, kept for reference)
`ultralytics` writes settings to a per-OS user config directory by default
(e.g. `%APPDATA%\Ultralytics\settings.json` on Windows), which can fail to
import in a sandboxed environment without write access there. This was hit
and fixed by having model-loading/training entry points set
`YOLO_CONFIG_DIR` to a project-local path before `ultralytics` is imported
(see `utils/ultralytics_config.py`, RULES.md R16). Not a currently-open
blocker — recorded so it isn't rediscovered as a new bug.

## Not blocked, but requires a `docs/DECISIONS.md` entry first
- Changing the severity-scoring formula in `pages/2_Upload_Analysis.py`.
- Changing frame-sampling rate in video/webcam analysis.
- Any change to `DAMAGE_CLASSES` accompanying a retrained model.

## How to lift a block
A human maintainer (repo owner) edits this file directly, states the reason
in the commit message, and — if the change is architectural — adds a row to
`docs/DECISIONS.md`. An AI assistant should never lift its own block.
