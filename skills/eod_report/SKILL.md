# EOD Report Skill

## Purpose

Create an end-of-day operating report for Aximo Control.

## When To Use

- At the end of a work session.
- After commits or pushes are completed.
- Before handing work to another session.

## Report Sections

- Date.
- Repository and branch.
- Executive summary.
- Completed tasks.
- Commits.
- Artifacts created or updated.
- Validation results.
- Secret/sensitive scan status.
- Push status.
- Task status summary.
- Machine warnings.
- Remaining blockers.
- Recommended next task.
- Next ChatGPT prompt.
- Next Codex prompt.
- Final operating state.

## Rules

- Keep the report internal by default.
- Do not send the report externally unless explicitly approved.
- State whether commits and pushes occurred.
- State whether the working tree is clean.
- Include next ChatGPT and Codex prompts that can restart work from repository files rather than hidden chat context.
