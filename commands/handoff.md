# Handoff Command

## Purpose

Transfer operating context to another human, agent, machine, or future session without relying on hidden chat history.

## Inputs

- Current task state.
- Relevant reports and dashboards.
- Recent commits.
- Known blockers.
- Files changed.
- Validation commands and results.

## Workflow

1. Confirm repository and branch.
2. Identify the latest relevant reports.
3. Summarize what changed and why.
4. List exact file paths for follow-up.
5. Record blockers and approval requirements.
6. Recommend the next task.

## Safety Rules

- Keep handoffs internal unless explicitly approved for external sharing.
- Do not include secrets or credentials.
- Do not imply work is complete unless validation supports it.
- Preserve uncertainty and open questions.

## Expected Output

- Handoff summary.
- Artifact list.
- Validation status.
- Blockers.
- Next action.

