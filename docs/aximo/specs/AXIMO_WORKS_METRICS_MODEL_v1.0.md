# AXIMO WORKS — METRICS_MODEL_v1.0

## 1. Purpose

This document defines the canonical Metrics Model of Aximo Works.

Metrics are derived exclusively from events.

Metrics serve four purposes:

1. Validate business value
2. Monitor operational health
3. Enforce SLA
4. Enable future billing

Metrics must NEVER mutate or override events.

---

# 2. Metric Categories

Metrics are grouped into five primary domains:

1. Business Value Metrics
2. Execution Health Metrics
3. SLA & Governance Metrics
4. Deployment Metrics
5. Financial Attribution Metrics (future-ready)

---

# 3. Business Value Metrics

These measure real customer-facing impact.

For LeadCapture_HVAC_Skill_v1.0:

- total_conversations
- leads_captured
- emergency_leads
- lead_conversion_rate (derived)
- avg_response_latency_ms

Derived Formulas:

lead_conversion_rate = leads_captured / total_conversations

These metrics validate whether the Skill solves a real business problem.

---

# 4. Execution Health Metrics

These measure runtime stability.

- executions_triggered
- executions_completed
- executions_failed
- failure_rate
- avg_execution_time_ms

Derived:

failure_rate = executions_failed / executions_triggered

Execution health must be monitored per deployment.

---

# 5. SLA & Governance Metrics

These measure policy enforcement.

- approval_requests
- approval_granted
- approval_rejected
- approval_timeout
- sla_breaches
- escalations_triggered
- pressure_invocations

Derived:

approval_delay_avg
sla_breach_rate

These metrics validate Control Plane effectiveness.

---

# 6. Deployment Metrics

These measure tenant-level operational state.

Per Deployment:

- deployment_status
- last_execution_timestamp
- error_rate
- current_skill_version
- version_upgrade_count

Per Customer:

- active_deployments
- total_event_volume

---

# 7. Financial Attribution Metrics (Future-Ready)

Although billing is not implemented in v1.0,
metrics must support monetization later.

Trackable Units:

- executions_per_customer
- actions_per_customer
- high_risk_actions_per_customer
- event_volume_per_customer

This enables future billing models such as:

- per deployment
- per execution
- per action
- per lead

---

# 8. Metric Derivation Rules

1. All metrics are derived from EVENT_MODEL_v1.0.
2. No metric may exist without event traceability.
3. Metrics must be customer-scoped.
4. Metrics aggregation must preserve isolation boundaries.

---

# 9. Monitoring Thresholds (Initial Guidance)

These are default alerting baselines.

- failure_rate > 5% → Warning
- failure_rate > 10% → Escalation
- avg_execution_time_ms > threshold → Warning
- sla_breach_rate > 3% → Escalation

Thresholds are configurable per deployment.

---

# 10. Relationship to Other Specifications

EVENT_MODEL_v1.0 → Source of truth
RUNTIME_CONTRACT_v1 → Defines measurable stages
CONTROL_PLANE_SPEC_v1 → Defines governance signals
DEPLOYMENT_MODEL_v1 → Defines tenant scoping

METRICS_MODEL_v1.0 defines how performance and value are quantified.

---

# 11. Invariants

1. Metrics must never override event data.
2. Metrics must be reproducible from event logs.
3. Customer isolation must be preserved in aggregation.
4. Metric calculation must be deterministic.

---

# 12. Status

Version: v1.0
Scope: Canonical Metrics Definition

This document establishes the measurement backbone of Aximo Works.
