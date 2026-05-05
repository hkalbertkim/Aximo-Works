# Task 012 Aximo Scaffold Review

## Review Goal

Review the Aximo-native operating scaffold created in Task 012 before commit. The review checks whether the scaffold is tool-agnostic, approval-gated, documentation-only where intended, and aligned with the Markdown/YAML/Python-first Aximo Control model.

## Files Reviewed

- `AXIMO.md`
- `commands/start_task.md`
- `commands/eod.md`
- `commands/handoff.md`
- `commands/weekly_review.md`
- `agents/dev_implementation_agent.md`
- `agents/validation_agent.md`
- `agents/report_agent.md`
- `agents/operations_agent.md`
- `skills/task_packet_creation/SKILL.md`
- `skills/validation_report/SKILL.md`
- `skills/eod_report/SKILL.md`
- `skills/git_discovery/SKILL.md`
- `adapters/chatgpt.md`
- `adapters/codex.md`
- `adapters/claude_code.md`
- `hooks/planned_events.md`

## Pass / Fail Checklist

| Criterion | Result | Notes |
| --- | --- | --- |
| Scaffold is Aximo-native, not Claude-specific | Pass | `AXIMO.md` is the canonical instruction file. `adapters/claude_code.md` explicitly says not to make `CLAUDE.md` canonical. |
| Tool adapters remain replaceable | Pass | ChatGPT, Codex, and Claude Code are described as adapters, and `AXIMO.md` names future replaceable tools. |
| Commit, push, PR, merge, deploy, external messages, settings changes, and secret/integration changes require explicit human approval | Pass | Approval boundaries are present across `AXIMO.md`, commands, agents, and adapters. |
| Non-development departments remain draft-only unless explicitly approved | Fail | The scaffold does not yet explicitly state that marketing, sales, customer support, docs/proposal, finance/admin, and other non-development outputs are draft-only until approved. |
| Commands behave as workflow entry points, not autonomous agents | Pass | Command files describe inputs, workflow, safety rules, and expected output. They do not grant autonomous authority. |
| Agents describe role boundaries and do not grant themselves external authority | Pass | Agent files define responsibilities and boundaries, with explicit restrictions on commits, pushes, external integrations, and settings changes. |
| Skills describe reusable capabilities, not hidden automation | Pass | Skill files define when to use the capability, report sections, rules, and outputs. No hidden automation is introduced. |
| Hooks define planned event vocabulary only and do not implement executable automation | Pass | `hooks/planned_events.md` explicitly states that event names are documentation only. |
| EOD workflow includes generation of next ChatGPT prompt and next Codex prompt | Fail | `commands/eod.md` and `skills/eod_report/SKILL.md` do not yet require next ChatGPT and next Codex prompts. |
| Scaffold preserves Markdown/YAML/Python-first model and does not introduce web app, database, external integration, or dependency | Pass | The scaffold is Markdown-only and does not add dependencies or executable integrations. |

## Issues Found

### Issue 1: Non-Development Departments Are Not Explicitly Draft-Only

The scaffold has strong approval boundaries for public-facing and external-facing outputs, but it does not directly state that non-development departments must produce drafts only unless explicitly approved.

Risk: marketing, sales, customer support, docs/proposal, finance/admin, or similar department work could be interpreted as ready for external use if the task packet is ambiguous.

Recommended severity: medium.

### Issue 2: EOD Workflow Missing Next ChatGPT And Codex Prompts

The EOD command and EOD skill both capture next actions, but neither requires generation of:

- Next ChatGPT prompt.
- Next Codex prompt.

Risk: future sessions may lose handoff quality or rely on hidden chat context rather than durable prompts.

Recommended severity: medium.

## Recommended Edits

1. Update `AXIMO.md` safety boundaries with a rule such as:

   `Non-development department outputs are draft-only unless explicitly approved for external use by a human.`

2. Update `commands/eod.md` expected output to include:

   - Next ChatGPT prompt.
   - Next Codex prompt.

3. Update `skills/eod_report/SKILL.md` report sections to include:

   - Next ChatGPT prompt.
   - Next Codex prompt.

4. Optionally update `agents/report_agent.md` to require clear draft/publication status for non-development reports.

## Approval Recommendation

Do not approve the scaffold as commit-ready until the two medium issues are fixed.

The scaffold is directionally correct and safe, but it should explicitly encode the draft-only rule for non-development departments and the next-prompt requirement for EOD workflows before becoming the durable operating baseline.

## Commit Recommendation

Fix first, then commit the scaffold and this review report together or in two focused commits:

1. `Add Aximo operating scaffold`
2. `Add scaffold review report`

If the recommended edits are made in the same pass, a single commit is also acceptable:

`Add Aximo operating scaffold and review`

## Suggested Next Task

Task 014 — Apply Aximo Scaffold Review Edits

Suggested scope:

- Add explicit draft-only language for non-development departments.
- Add next ChatGPT prompt and next Codex prompt requirements to EOD workflow docs.
- Re-run scaffold validation.
- Review the updated scaffold before committing.

