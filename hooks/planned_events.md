# Planned Event Names

## Purpose

Define future Aximo event names without implementing executable hooks.

These are placeholders for future design. They must not be treated as active automation, shell hooks, external service triggers, or notification integrations.

## Task Events

- `task.created`
- `task.started`
- `task.blocked`
- `task.completed`
- `task.moved`
- `task.reopened`

## Report Events

- `report.created`
- `report.updated`
- `daily_start.created`
- `daily_close.created`
- `eod_report.created`
- `handoff.created`

## Validation Events

- `validation.started`
- `validation.passed`
- `validation.failed`
- `validation.blocked`

## Machine Events

- `machine.status_checked`
- `machine.warning_detected`
- `machine.capacity_reviewed`

## Git Events

- `git.discovery_completed`
- `git.diff_reviewed`
- `git.commit_created`
- `git.push_completed`

## Rules

- Event names are documentation only.
- Do not add executable hook files without explicit approval.
- Do not connect events to external services without explicit approval.
- Do not store secrets or credentials in event definitions.

