# Aximo Control Transition

## Purpose

Aximo-Works is transitioning toward an Aximo Control-centered repository direction.

The existing repository began as an execution-pressure and work-push system for assigning, approving, and tracking work. That runtime history remains valuable and must be preserved while the repository gains a local file-based operating scaffold for portfolio, machine, agent, task, validation, and reporting control.

## Current Transition Approach

- Existing runtime and application materials are preserved for review.
- The Aximo Control scaffold is being added as a non-destructive operating layer.
- No force push has been performed.
- No destructive replacement has been performed.
- No archive action has been performed.
- No existing runtime, backend, frontend, operations, Telegram, Linear, launchd, or deployment files have been intentionally removed.

## Aximo Control Layer

The Control layer is Markdown/YAML/Python-first and includes:

- `AXIMO.md` for repository-level operating instructions.
- `commands/` for workflow entry points.
- `agents/` for role boundaries.
- `skills/` for reusable operating capabilities.
- `adapters/` for replaceable tool-specific guidance.
- `hooks/planned_events.md` for future event vocabulary only.
- `config/`, `dashboards/`, `tasks/`, `projects/`, `reports/`, and `templates/` for local operating state.

## Existing Runtime Layer

Existing Aximo-Works runtime and application materials remain in place for later review, including:

- `backend/`
- `frontend/`
- `aximo/`
- `ops/`
- existing `docs/`
- existing scripts and runbooks

These files should not be archived, removed, or replaced until a separate migration plan is reviewed and explicitly approved.

## Approval Boundaries

Explicit approval is required before:

- Pushing a transition branch.
- Opening a PR.
- Merging.
- Force pushing.
- Moving or archiving existing runtime files.
- Replacing the repository README.
- Changing repository settings.
- Adding dependencies.
- Connecting external services.
- Deploying or running production operations.

## Recommended Next Step

Review the transition branch locally, validate the Control scaffold, and decide whether to commit the non-destructive scaffold addition before any remote push or PR.

