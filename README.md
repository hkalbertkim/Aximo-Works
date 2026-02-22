# Aximo

Fire All the Idiots. Keep the Work.

Aximo is a 30-minute setup AI admin worker for SMB founders.
It replaces daily admin/ops work so founders can run a company alone.

## v0.1 Scope (LOCKED)
- Messenger: Slack (primary) + Telegram (daily brief only)
- Ingestion: Gmail read-only (ONLY one data source for v0.1)
- Answers ONLY 3 questions:
  1) What should I do today?
  2) What did we decide?
  3) What is at risk next?
- Outputs:
  - Meeting summary → action items
  - Daily brief (once/day)
- Guardrails:
  - No autonomous external sending
  - Keep responses short (<= 5 lines unless asked)
  - If uncertain, say so and ask a clarifying question

## Non-goals (v0.1)
- No CRM write
- No external email sending
- No advanced configuration
- No platform/marketplace features
- No graph/visualization

## Infra (internal, not customer-facing)
- OpenClaw (hosted on Alibaba Cloud initially)
- Later: migrate infra to Krako when ready (transparent to customer)
