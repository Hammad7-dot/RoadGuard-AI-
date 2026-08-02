# Project Rules

## Engineering Rules

- Keep changes spec-driven: every feature or behavioral fix needs acceptance criteria before implementation.
- Keep Streamlit page logic thin when practical; move reusable logic into `ai/`, `database/`, `components/`, or `utils/`.
- Do not hardcode demo metrics when real repository data is available.
- Do not commit generated files such as databases, uploaded media, processed videos, annotated outputs, caches, or local settings.
- Preserve model-loading through `ai/model_loader.py` so the YOLO model remains cached by Streamlit.
- Use parameterized SQL only.
- Close SQLite connections after reads and writes.
- Keep image arrays in RGB for Streamlit display and convert to BGR only when saving with OpenCV.
- Treat geolocation data as sensitive; only attach coordinates when explicitly available or entered by the user.

## Testing Rules

- Run `python -m compileall .` before submitting a change.
- For dependency smoke checks in restricted environments, set `YOLO_CONFIG_DIR` to a writable project path.
- Add tests for new pure logic.
- Use temporary databases for repository tests.
- Manually verify affected Streamlit pages when UI, uploads, video, reports, maps, or camera behavior changes.

## Documentation Rules

- Update `README.md` or `docs/` when setup, commands, user workflows, database shape, or output locations change.
- Document any manual test that cannot be automated yet.
- Keep docs command-first and specific to this repository.

## Safety Rules

- Do not overwrite the trained model file without an explicit model update spec.
- Do not delete detection history from user environments except through the app's intentional delete workflow.
- Do not add network calls for uploaded media or location data unless documented and approved.
- Do not weaken confidence thresholds or severity behavior without updating acceptance criteria and reports.
