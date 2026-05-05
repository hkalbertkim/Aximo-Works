# Codex Adapter

## Purpose

Describe how Codex should operate within Aximo workflows without making Aximo Control depend on Codex.

## Usage Boundary

- Use Codex for local repository edits, validation commands, report generation, and controlled git workflows.
- Prefer repo-native scripts and existing Markdown/YAML/Python patterns.
- Report commands run, files changed, validation results, and git status.

## Constraints

- Do not modify unrelated repositories.
- Do not commit, push, create PRs, merge, deploy, or change settings unless explicitly instructed.
- Do not add dependencies without approval.
- Do not treat planned hooks as executable automation.

## Expected Handoff

Codex should leave durable local artifacts in Aximo Control so ChatGPT, Claude Code, Gemma Coder, OpenClaw, or future adapters can continue from files rather than chat memory.

