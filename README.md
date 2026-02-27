<p align="center">
  <img src="assets/Aximo_Horizontal_Logo_Color.png" alt="AXIMO by Aximo Works" width="600" />
</p>

<p align="center">
  <b>AXIMO</b> — Execution Pressure Operating System  
  Built by <b>Aximo Works</b>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-BSL%201.1-blue" alt="License"></a>
  <img src="https://img.shields.io/badge/status-ExecutionOS%20v1-green" alt="Status">
  <img src="https://img.shields.io/badge/mode-SingleFounder-orange" alt="Mode">
</p>

---

# Why AXIMO Exists

Most small companies do not collapse because of lack of intelligence.

They collapse because execution depends on:

- Memory
- Mood
- Follow-ups
- Emotional escalation
- The founder’s personal energy

In early-stage teams:

- Tasks are assigned verbally.
- Deadlines are flexible.
- Avoidance has no structural consequence.
- Follow-up depends on the founder.
- Silence is invisible.

The founder becomes:

- A reminder system  
- A human escalation engine  
- A bottleneck  

Execution decays quietly.

AXIMO exists to replace emotional pressure with structural pressure.

---

# What AXIMO Is

AXIMO is **not** a productivity app.  
It is not a chat assistant.  
It is not a project management dashboard.

AXIMO is a:

> Deterministic Execution Operating System.

It converts communication into:

- Explicit state transitions  
- Measurable execution pressure  
- Logged accountability  
- Scheduled escalation  
- Structural transparency  

Autonomy is not culture.  
Autonomy is enforced structure.

---

# Current State — Execution OS v1

AXIMO is currently operating in:

> **Single-Founder Mode (Phase 1 Locked)**

The system is:

- Deterministic  
- Auditable  
- Telegram-integrated  
- Pressure-scored  
- Scheduled  
- Launchd-managed  
- Production-stable  

This is not a prototype anymore.  
It is a functioning execution loop.

---

# How the System Works

## 1. Explicit State Machine

Every task exists in one of four states:

```
pending_approval
approved
rejected
done
```

Rejected is not a note.  
It is a structural state.

State transitions are recorded.  
Nothing disappears silently.

---

## 2. Approval Gate

Execution cannot proceed without approval.

This removes ambiguity:

- No "I thought you meant…"
- No "I’ll do it later."
- No invisible backlog accumulation.

---

## 3. Audit Layer

All structural transitions are logged in `task_events`.

Each event records:

- from_status
- to_status
- actor
- reason
- timestamp

AXIMO is fully auditable.

This is not surveillance.  
It is structural memory.

---

## 4. Execution Pressure (P2 Model)

AXIMO calculates dynamic execution pressure:

```
P2 = ceil(weight × priority_factor × timeScore)
```

Priority factor:

- high → 2.0  
- medium → 1.0  
- low → 0.5

TimeScore buckets:

- overdue  
- due soon  
- upcoming  
- no due

Escalation policy (v1):

- status = pending_approval  
- P2 > 0  
- Top 3 tasks  
- Telegram push  
- 09:00 / 13:00 local time  

Silence becomes measurable.

Neglect becomes visible.

Pressure becomes structural — not emotional.

---

# Control Loop

Founder  
→ Task created  
→ Approval gate  
→ Execution  
→ Audit log  
→ Pressure scoring  
→ Scheduled escalation  
→ Telegram feedback  

The loop is closed.

The founder stops chasing.

The system applies consistent pressure.

---

# Architecture

Backend:
- FastAPI
- SQLite
- Launchd-managed service
- Webhook-driven Telegram integration

Frontend:
- Next.js
- 4-column Kanban state model
- Debug toggle system
- Pressure visualization

Scheduler:
- launchd calendar triggers
- telegram_pressure_alert.py

Security:
- Cloudflare Access
- Webhook secret validation

LLM:
- Ollama (local inference)

Public entry (protected):
https://meeting.aximo.works

---

# Roadmap

## Phase 1 — Execution Pressure (Complete)
- Deterministic approval gate
- Explicit rejected state
- Audit trail
- Pressure scoring
- Scheduled escalation

## Phase 2 — Multi-Operator Mode
- Owner-based segmentation
- Escalation hierarchy
- Delay detection logic
- Overdue forced inclusion

## Phase 3 — Transparency Layer
- Execution analytics
- Behavioral pattern detection
- Risk heatmaps

## Phase 4 — Autonomous Company OS

The ultimate goal:

> Enable a founder to operate a company solo —  
> or with a very small team —  
> while maintaining execution consistency at scale.

Execution Pressure → Transparency → Automation → Autonomy.

---

# Documentation

- `docs/aximo/specs/` — System specifications  
- `docs/aximo/skills/` — Skill contracts  
- `docs/runbooks/` — Operational guides  
- `docs/reports/` — Context snapshots  

---

# License

This project is source-available under the Business Source License 1.1 (BSL 1.1).

Internal use and evaluation permitted.  
No competing hosted service prior to Change Date.

Converts to Apache 2.0 on 2029-01-01.
