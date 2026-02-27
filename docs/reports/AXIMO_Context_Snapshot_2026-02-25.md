# AXIMO WORKS — Context Snapshot & EOD
## Date: 2026-02-25
## Mode: Single-Founder Execution Model (Phase 1 Locked)

---

# 0. Purpose of This Document

This document is not just an EOD summary.
It is a **Context Transfer Snapshot**.

It contains:

• Architectural decisions  
• Problem history  
• Failure points encountered  
• Current system state  
• Operational philosophy  
• Deferred roadmap  

This document is designed so that a **new conversation can resume development without losing strategic context**.

---

# 1. Strategic Positioning (Locked Today)

AXIMO is currently positioned as a:

> Single-Founder Execution Pressure Operating System

It is NOT:

• A generic productivity tool  
• A team collaboration dashboard  
• A chat-based assistant

It IS:

• Deterministic execution engine  
• Human approval gate system  
• Pressure-based prioritization model (P2)  
• Telegram command + escalation loop  
• Fully auditable state machine

Multi-owner escalation logic is intentionally deferred to Phase 2.

---

# 2. Architecture Overview (Current State)

## Backend

• FastAPI  
• SQLite (aximo.db)  
• Launchd-managed service  
• Webhook-driven Telegram integration  
• Deterministic task execution

## Frontend

• Next.js (Kanban UI)  
• 4-column state model  
• Debug toggle system  
• Pressure visualization (P2 scoring)

## Scheduler

• launchd-based calendar trigger  
• 09:00 local time  
• 13:00 local time  
• telegram_pressure_alert.py

## Control Loop

Founder → Task Created → Approval Gate → Execution → Audit → Pressure Escalation → Telegram Feedback

System loop is closed and stable.

---

# 3. Status Machine Evolution (Critical Refactor)

Previous Model:

• pending_approval  
• approved  
• done

Problem:

Rejected tasks were only annotated, not structurally separated.
This caused:

• UI ambiguity  
• Audit confusion  
• Escalation misclassification

New Model:

• pending_approval  
• approved  
• rejected  
• done

Changes Implemented:

• reject_task_internal now sets status = "rejected"  
• Kanban Rejected column added  
• Grid layout changed 3 → 4 columns  
• Status transitions cleaned

This was a structural stabilization milestone.

---

# 4. Audit Layer (task_events)

New table:

• id (uuid)  
• task_id  
• event_type  
• from_status  
• to_status  
• actor  
• reason  
• created_at

Logged events:

• status_changed  
• approved  
• rejected

Critical Debug History:

• Insert not committing  
• Stray duplicate inserts  
• IndentationError causing 500  
• Partial launchd reload instability

All resolved.

Event persistence verified via DB inspection.

System now auditable.

---

# 5. Debug Infrastructure

Frontend:

• Debug ON/OFF toggle  
• Verbose diagnostics hidden by default  
• localStorage persistence

Backend:

• AXIMO_DEBUG_EVENTS flag  
• EVENTLOG output gated  
• Production-safe logging

Debug noise removed from normal operation.

---

# 6. Execution Pressure Engine (v1)

P2 formula:

P2 = ceil(weight × priority_factor × timeScore)

priority_factor:

• high → 2.0  
• medium → 1.0  
• low → 0.5

TimeScore buckets:

• overdue  
• due_soon  
• upcoming  
• no_due

Escalation filter:

• status = pending_approval  
• P2 > 0

Output:

• Top 3 tasks  
• Telegram push  
• 09:00 / 13:00 local time

LaunchAgent verified.
Manual kickstart verified.
Telegram delivery verified.

---

# 7. Infrastructure Corrections Made Today

• Cloudflared persistence stabilized  
• Webhook secret mismatch resolved  
• 401/530 issues eliminated  
• Local path artifacts removed from Git  
• .gitignore corrected  
• Linear HKA-83 created and marked Done

System is operational.

---

# 8. Known Technical Artifacts

• Legacy tasks may contain reject_reason with status=pending_approval
  (Pre-refactor artifact)

• Backup .bak files exist locally but ignored by git

These are non-blocking.

---

# 9. Phase 2 (Deferred by Design)

Not implemented intentionally:

1. Overdue forced inclusion in escalation
2. Owner-based pressure segmentation
3. 24-hour approval delay detection
4. Multi-owner escalation hierarchy
5. Adaptive pressure thresholds
6. Pressure heatmap analytics

These belong to Multi-Operator Mode.

---

# 10. System Classification at End of Day

AXIMO Execution OS v1:

• Deterministic  
• Founder-centric  
• Auditable  
• Scheduled  
• Stable  
• Git-clean  
• Linear-synced

AXIMO is now a functioning Execution Pressure Operating System.

---

# 11. Starting Point for Next Conversation

Next logical directions:

A. Escalation logic refinement (Overdue weighting)  
B. Owner segmentation (Phase 2 foundation)  
C. UI simplification (production mode)  
D. Execution metrics dashboard  
E. Automatic stale task detection  

Context is fully captured.

---

End of Context Snapshot.
