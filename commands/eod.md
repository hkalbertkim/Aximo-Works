# EOD Command

## Purpose

Close an operating day by recording completed work, generated artifacts, task state, warnings, validation results, and recommended next actions.

## Inputs

- Daily start report if available.
- Task dashboard if available.
- Machine status report if available.
- Project discovery report if available.
- Git status and recent commits.
- Known blockers and follow-up tasks.

## Workflow

1. Confirm repository status.
2. Review completed tasks and generated artifacts.
3. Summarize task status counts.
4. Summarize blocked tasks.
5. Summarize machine and project warnings.
6. Record validation commands and outcomes.
7. Record whether commits or pushes occurred.
8. Generate the next ChatGPT prompt for continuity.
9. Generate the next Codex prompt for local execution continuity.
10. Write or update the daily close report.

## Safety Rules

- Do not send external messages.
- Do not push unless explicitly requested.
- Do not include secrets, credentials, customer data, or sensitive infrastructure details.
- Keep the report factual and auditable.

## Expected Output

- Daily close report path.
- Summary of completed work.
- Validation result.
- Current git status.
- Recommended next task.
- Next ChatGPT prompt.
- Next Codex prompt.
