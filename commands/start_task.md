# Start Task Command

## Purpose

Start a bounded Aximo Control task with clear scope, safety boundaries, expected artifacts, and validation requirements.

## Inputs

- Task title or task ID.
- Target repository or Aximo Control path.
- Relevant project, machine, and department.
- Allowed files or directories.
- Explicit approval boundaries.
- Expected report or dashboard updates.

## Workflow

1. Confirm the current working directory and repository status.
2. Read relevant task, project, dashboard, and report files.
3. Identify whether the task affects only Aximo Control or an external project repository.
4. State the implementation plan if the task is broad or risky.
5. Make the smallest useful change.
6. Run local validation commands.
7. Report changed files, validation results, warnings, and next action.

## Safety Rules

- Do not modify unrelated repositories.
- Do not commit or push unless explicitly instructed.
- Do not create external service connections.
- Do not introduce dependencies unless explicitly approved.
- Preserve existing user or agent changes.

## Expected Output

- Commands run.
- Files changed.
- Validation result.
- Remaining risks or blockers.
- Recommended next step.

