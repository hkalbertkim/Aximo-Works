<p align="center">
  <img src="assets/KORA_Img_Text_logo.png" alt="KORA Logo" width="220" />
</p>

<h1 align="center">KORA</h1>

<p align="center"><strong>Inference-First Execution Architecture</strong></p>

<p align="center">
  <img alt="Deterministic-first" src="https://img.shields.io/badge/Deterministic--first-0f766e?style=flat-square" />
  <img alt="DAG execution" src="https://img.shields.io/badge/DAG-execution-1d4ed8?style=flat-square" />
  <img alt="Budget governance" src="https://img.shields.io/badge/Budget-governance-7c3aed?style=flat-square" />
  <img alt="Telemetry" src="https://img.shields.io/badge/Telemetry-observability-475569?style=flat-square" />
  <img alt="Model-agnostic" src="https://img.shields.io/badge/Model-agnostic-374151?style=flat-square" />
</p>

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

## Local CLI usage
1. Install deps: `python3 -m pip install -r requirements.txt`
2. Set env:
   - `export SLACK_BOT_TOKEN="xoxb-your-token"`
   - `export SLACK_CHANNEL="#new-channel"` (optional)
3. Run commands:
   - `python3 aximo_cli.py today`
   - `python3 aximo_cli.py decided`
   - `python3 aximo_cli.py risk`
