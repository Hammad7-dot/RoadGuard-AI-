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

## Not blocked, but requires a `docs/DECISIONS.md` entry first
- Changing the severity-scoring formula in `pages/2_Upload_Analysis.py`.
- Changing frame-sampling rate in video/webcam analysis.
- Any change to `DAMAGE_CLASSES` accompanying a retrained model.

## How to lift a block
A human maintainer (repo owner) edits this file directly, states the reason
in the commit message, and — if the change is architectural — adds a row to
`docs/DECISIONS.md`. An AI assistant should never lift its own block.
