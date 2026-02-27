# AXIMO WORKS — EVENT_MODEL_v1.0

## 1. Purpose

This document defines the canonical Event Model of Aximo Works.

Events are the immutable source of truth for:

- Execution traceability
- Audit compliance
- SLA monitoring
- Metrics derivation
- Billing attribution (future)

Every execution, approval, escalation, and action MUST emit structured events.

---

# 2. Core Principles

1. Events are append-only.
2. Events are immutable once written.
3. Events are always scoped by customer_id.
4. Events are attributable to deployment_id and skill_version.
5. Governance decisions must also emit events.

---

# 3. Event Categories

Events are grouped into five primary categories.

## 3.1 Execution Events

- execution_triggered
- execution_processing
- execution_completed
- execution_failed

---

## 3.2 Action Events

- action_prepared
- action_dispatched
- action_failed

---

## 3.3 Approval Events

- approval_requested
- approval_granted
- approval_rejected
- approval_timeout

---

## 3.4 SLA & Governance Events

- sla_breached
- escalation_triggered
- pressure_invoked
- deployment_suspended

---

## 3.5 Deployment Lifecycle Events

- deployment_created
- deployment_configured
- deployment_activated
- deployment_updated
- deployment_terminated
- version_upgraded
- version_rolled_back

---

# 4. Canonical Event Schema (Conceptual)

Every event must include:

- event_id (UUID)
- event_type
- timestamp (UTC)
- customer_id
- deployment_id
- skill_id
- skill_version
- execution_id (nullable for lifecycle events)
- risk_level (if applicable)
- approval_mode (if applicable)
- actor (system / founder / operator / external_user)
- payload (structured JSON)

Optional fields:

- correlation_id
- channel_type
- error_code
- latency_ms

---

# 5. Event Flow Within Execution

Standard execution produces the following minimum sequence:

1. execution_triggered
2. execution_processing
3. action_prepared
4. action_dispatched
5. execution_completed

If approval required:

1. execution_triggered
2. execution_processing
3. approval_requested
4. approval_granted / approval_rejected
5. action_dispatched (if approved)
6. execution_completed

---

# 6. Event Storage Model

Events must be stored in an append-only store.

Minimum requirements:

- Indexed by customer_id
- Indexed by deployment_id
- Indexed by timestamp
- Queryable by event_type

Initial implementation may use relational storage (e.g., SQLite).
Future evolution may support streaming or event-sourcing infrastructure.

---

# 7. Replay & Audit

The system must support:

- Full execution trace reconstruction
- Approval decision history
- Deployment version history

Events must be sufficient to reconstruct execution outcomes.

---

# 8. Observability & Metrics Integration

Metrics derive from events.

Examples:

- Lead count = count(action_dispatched where action_type=lead_capture)
- Error rate = execution_failed / execution_triggered
- SLA breach rate = sla_breached / execution_completed

Metrics must never mutate events.

---

# 9. Invariants

1. No execution completes without emitting execution_completed or execution_failed.
2. Approval decisions must emit approval events.
3. All action dispatch must emit action_dispatched or action_failed.
4. Events cannot be updated or deleted.
5. Cross-customer event access is forbidden.

---

# 10. Relationship to Other Specifications

SYSTEM_MAP_v1 defines structural layers.
SKILL_LIFECYCLE_SPEC_v1 defines state transitions.
DOMAIN_MODEL_v1 defines entity ownership.
CONTROL_PLANE_SPEC_v1 defines governance rules.
RUNTIME_CONTRACT_v1 defines execution flow.

EVENT_MODEL_v1.0 defines traceability and audit backbone.

---

# 11. Status

Version: v1.0
Scope: Canonical Event Definition

This version establishes immutable event structure and categories.
Future versions may extend schema fields but must remain backward compatible.

