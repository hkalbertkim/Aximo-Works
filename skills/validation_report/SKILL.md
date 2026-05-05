# Validation Report Skill

## Purpose

Create a validation report that records what was checked, what passed, what failed, and what should happen next.

## When To Use

- After running smoke tests.
- After inspecting a dirty working tree.
- After generating dashboards or reports.
- Before moving a task to `done` or `blocked`.

## Report Sections

- Goal.
- Context.
- Commands run.
- Results.
- Warnings.
- Files changed.
- Task movement recommendation.
- Next action.

## Rules

- Separate observed facts from recommendations.
- Do not claim full validation if any recorded validation command failed or was skipped.
- Record blockers explicitly.
- Do not include secrets or sensitive output.

