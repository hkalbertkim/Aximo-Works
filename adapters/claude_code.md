# Claude Code Adapter

## Purpose

Describe how Claude Code can participate in Aximo workflows without making Aximo Control Claude-specific.

## Usage Boundary

- Use Claude Code as one replaceable local coding adapter.
- Follow `AXIMO.md`, command files, agent role files, and skill files.
- Keep generated artifacts compatible with other tools.

## Constraints

- Do not create or require `CLAUDE.md` as the canonical operating file for this repository.
- Do not add Claude-specific hooks or settings without explicit approval.
- Do not use tool-specific behavior that prevents Codex, ChatGPT, Gemma Coder, OpenClaw, or future tools from operating on the same files.
- Do not commit or push unless explicitly instructed.

## Expected Handoff

Claude Code work should end with plain Markdown/YAML/Python artifacts, validation results, and clear task state.

