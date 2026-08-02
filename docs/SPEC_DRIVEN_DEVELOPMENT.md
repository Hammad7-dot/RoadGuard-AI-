# Spec-Driven Development

RoadGuard AI should treat every meaningful change as a small product specification before code is written. This keeps the Streamlit UI, YOLO inference flow, database records, and reports aligned.

## Workflow

1. Start with a spec.
   - Define the user problem.
   - Define the expected behavior.
   - Define non-goals so the change stays scoped.
   - Define acceptance criteria that can be tested.

2. Design the implementation.
   - Identify touched modules, pages, database tables, model assets, and generated outputs.
   - Note data flow changes from upload/live/video input through detection, persistence, dashboard, and reporting.
   - Call out migration, privacy, or performance risks.

3. Write or update tests.
   - Add unit tests for pure logic such as summaries, confidence calculations, severity rules, and repository transforms.
   - Add integration checks for database writes, report generation, and model-loading boundaries.
   - Add manual verification steps for Streamlit pages and computer-vision output.

4. Implement narrowly.
   - Keep code changes focused on the spec.
   - Prefer existing project structure and helpers.
   - Avoid unrelated formatting or broad refactors.

5. Verify and document.
   - Run syntax checks and available automated tests.
   - Record manual checks when model inference, camera access, or uploaded media are involved.
   - Update README or docs when commands, behavior, data schema, or workflows change.

## Spec Template

```markdown
# Spec: <Feature or Fix Name>

## Problem
What user or maintainer problem are we solving?

## Goals
- What must be true when this ships?

## Non-Goals
- What is intentionally outside scope?

## User Flow
1. User action.
2. System behavior.
3. Result shown or stored.

## Data and Model Impact
- Inputs:
- Outputs:
- Database changes:
- Model or inference changes:

## Acceptance Criteria
- [ ] Observable behavior 1.
- [ ] Observable behavior 2.
- [ ] Error/empty state covered.
- [ ] Tests or manual checks documented.

## Test Plan
- Automated:
- Manual:

## Rollback Plan
How can this be disabled or reverted safely?
```

## Definition of Ready

- The problem, expected behavior, and affected users are clear.
- Acceptance criteria are testable.
- Required assets, model files, sample media, and environment variables are available.
- Any schema or persistence change includes a migration plan.

## Definition of Done

- Acceptance criteria are satisfied.
- `python -m compileall .` passes.
- `python -m unittest discover -s tests` passes.
- Dependency imports pass.
- New logic has tests where practical.
- Streamlit pages touched by the change have been manually checked.
- Documentation is updated for user-facing behavior or setup changes.
