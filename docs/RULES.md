# Engineering Rules — RoadGuard AI

These are enforced rules, not suggestions. A PR that violates one of these
without a corresponding `docs/DECISIONS.md` entry should be rejected in
review.

## R1 — Spec before code
No feature or behavior change merges without a matching update to
`docs/SPEC.md`. If the spec doesn't say it, it isn't intended behavior.

## R2 — Color space discipline
Any function that receives or returns a video/image frame as a numpy array
must document whether it is RGB or BGR in its docstring, and conversions
must happen at the boundary (model output → RGB, before display or save).
Do not convert ad hoc inside UI code. (Root cause of a real historical bug.)

## R3 — No fake data in the UI
Every number, chart, or stat shown in `pages/*.py` or `components/*.py`
must originate from a live call into `database/repository.py`. Placeholder
or mocked values are only acceptable behind an explicit `DEMO_MODE` flag
that does not exist yet — don't add hardcoded numbers silently.

## R4 — DB schema is additive-only
`database/database.py::_migrate_schema()` may only add columns. Never drop
or rename a column in place. Renames = add new column, migrate data, mark
old column deprecated in `docs/DECISIONS.md`, remove in a later major change
with its own migration.

## R5 — Class list must match model weights
`utils/constants.py::DAMAGE_CLASSES` must always equal `model.names` for
whatever `.pt` file `MODEL_PATH` points to. Verify this manually whenever
`best.pt` is replaced.

## R6 — Single source of truth for paths and constants
Model path, DB path, and damage classes are each defined once
(`utils/constants.py`, `database/database.py`). No second hardcoded copy
anywhere else in the codebase.

## R7 — Dependency pins are load-bearing
`requirements.txt` pins (especially `av`, `ultralytics`, `opencv-python-headless`)
resolve specific past breakages (see D6). Do not loosen a pin without
testing a fresh install on a clean environment first.

## R8 — Idempotent scripts
Anything in `scripts/` must be safe to run twice in a row with no
side-effect difference between the first and second run.

## R9 — No secrets committed
No API keys, credentials, or `.env` files in the repo. `.gitignore` must
keep `uploads/`, `outputs/`, `reports/`, and `*.db` out of version control
unless a file is explicitly meant as a fixture.

## R10 — Test before merge
At minimum: `python -m py_compile` (or equivalent) on all changed files,
and a manual run-through of any UI page touched. Log what was checked in
`docs/TEST_REPORT.md` for anything non-trivial.

## R11 — Respect the handbrake
Some actions are hard-blocked regardless of who asks or how urgently.
See `docs/handbrake-blocked.md`. These are not "ask a human first" —
they are "do not do this in this repo, period" until that file is
explicitly revised by the maintainer.
