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

## R12 — Thin pages, logic in modules
Keep `pages/*.py` focused on layout and wiring. Reusable logic belongs in
`ai/`, `database/`, `components/`, or `utils/`, not duplicated inline
across pages.

## R13 — Parameterized SQL only
Every query in `database/` uses `?` placeholders — never string-interpolate
user input (filenames, search terms, coordinates) into SQL.

## R14 — Close connections
Every `get_connection()` call is paired with `conn.close()` on every code
path, including error paths.

## R15 — Geolocation is sensitive by default
Only attach latitude/longitude to a detection when it was explicitly read
from EXIF or entered by the user (see `use_location` checkbox in
`pages/2_Upload_Analysis.py`). Never infer or guess coordinates.

## R16 — Local Ultralytics config
`ultralytics` writes settings to a per-OS user config dir by default, which
can fail to import in sandboxed/restricted environments (e.g. no write
access to `%APPDATA%\Ultralytics` on Windows). Model-loading and training
entry points must configure `YOLO_CONFIG_DIR` to a project-local writable
path (see `utils/ultralytics_config.py`) *before* `ultralytics` is
imported, so the app doesn't fail to start in a fresh environment.

## R17 — Test command for this repo
Before submitting a change: `python -m compileall .` must pass. If working
in a restricted environment, set `YOLO_CONFIG_DIR` first (see R16). Add
unit tests for new pure logic (e.g. `tests/test_detector_metrics.py`) and
use a temporary/throwaway database for repository tests — never the real
`database/roadguard.db`.

## R18 — Manual verification for UI-affecting changes
Any change touching uploads, video, live camera, reports, maps, or
dashboard behavior needs a manual click-through of the affected page(s) —
py_compile passing is necessary but not sufficient. Record what was
checked in `docs/TEST_REPORT.md`.

## R19 — Keep docs in sync with behavior
Update `README.md` and/or `docs/` whenever setup steps, commands, user
workflows, the database schema, or output file locations change. Document
any manual test that can't yet be automated. Docs should be
command-first and specific to this repo, not generic boilerplate.
