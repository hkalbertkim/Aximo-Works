# Aximo Operating Instructions

## Purpose

Aximo Control is the local operating control plane for coordinating projects, machines, agents, tasks, validations, and reports. This repository should remain Markdown/YAML/Python-first, private by default, and report-driven.

This file is the repo-level operating instruction file for any compatible assistant or coding tool. It is intentionally tool-agnostic: Claude Code, Codex, ChatGPT, Gemma Coder, OpenClaw, and future tools should operate through replaceable adapters rather than hard-coded assumptions.

## Operating Model

- Use Markdown for human-readable operating documents.
- Use YAML for structured local state.
- Use Python standard library scripts for local automation when needed.
- Keep workflows file-based until there is a clear reason to add more infrastructure.
- Prefer small, reviewable changes with explicit reports.
- Keep commands, agents, skills, adapters, and hooks as documentation unless explicitly approved for implementation.

## Safety Boundaries

- Do not add secrets, tokens, credentials, private keys, customer data, production credentials, or sensitive infrastructure details.
- Do not connect external services unless explicitly requested and approved.
- Do not commit, push, create PRs, merge, deploy, publish, or change repository settings unless explicitly instructed.
- Do not modify project repositories discovered by Aximo Control unless the current task explicitly targets that repository.
- Public-facing, customer-facing, investor-facing, or partner-facing outputs require human approval.
- Non-development department outputs are draft-only unless explicitly approved for external use by a human. This includes marketing, sales, customer support, docs/proposal, finance/admin, and other non-development operating outputs.

## Workflow Entry Points

- Start work with `commands/start_task.md`.
- Close daily work with `commands/eod.md`.
- Transfer context with `commands/handoff.md`.
- Review operating health with `commands/weekly_review.md`.

## Role Boundaries

- Development implementation work should follow `agents/dev_implementation_agent.md`.
- Validation work should follow `agents/validation_agent.md`.
- Report creation should follow `agents/report_agent.md`.
- Control-plane operations should follow `agents/operations_agent.md`.

## Reusable Skills

- Task packet creation: `skills/task_packet_creation/SKILL.md`
- Validation reporting: `skills/validation_report/SKILL.md`
- EOD reporting: `skills/eod_report/SKILL.md`
- Git discovery: `skills/git_discovery/SKILL.md`

## Tool Adapters

Adapters describe how tools should map into Aximo workflows without making Aximo depend on one tool:

- ChatGPT: `adapters/chatgpt.md`
- Codex: `adapters/codex.md`
- Claude Code: `adapters/claude_code.md`

## Planned Events

Future event names are documented in `hooks/planned_events.md`. They are not executable hooks and must not be treated as automation until explicitly implemented and approved.
