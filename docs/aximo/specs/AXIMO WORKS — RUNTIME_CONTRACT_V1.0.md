# AXIMO WORKS — RUNTIME_CONTRACT_v1

## 1. Purpose

This document defines the execution contract of the Agent Runtime.

The Runtime is responsible for executing Skills in a channel-agnostic manner.

It does not define governance rules.
Governance is handled by the Control Plane.

---

# 2. Execution Skeleton

All Skills execute using the same pipeline:

Input → Preprocess → Context Injection → Skill Logic → LLM Call → Postprocess → Action Dispatch → Event Emission

Each stage must be modular and replaceable.

---

# 3. Stage Definitions

## 3.1 Input

Normalized input from Channel Adapter.

Includes:
- Payload
- Channel metadata
- Deployment reference

---

## 3.2 Preprocess

- Input validation
- Normalization
- Basic sanitization

---

## 3.3 Context Injection

Build execution context using:
- Deployment configuration
- Knowledge sources
- Historical events
- External data sources

---

## 3.4 Skill Logic

Skill-specific transformation rules.

Defines:
- Intent detection
- Branching logic
- Action planning

---

## 3.5 LLM Call

LLM invocation with:
- Structured prompt
- Guardrails
- Output schema expectations

LLM must return structured output where possible.

---

## 3.6 Postprocess

- Output validation
- Risk tagging
- Action preparation

---

## 3.7 Action Dispatch

Dispatch actions to:
- Email systems
- Sheets/CRM
- Task systems
- Notification channels

Action execution must emit events.

---

## 3.8 Event Emission

Emit structured events for:
- Execution started
- Execution completed
- Action dispatched
- Execution failed

Events must include:
- Deployment ID
- Skill Version
- Timestamp
- Risk level
- Outcome status

---

# 4. Channel Adapter Contract

Each Channel Adapter must:

- Normalize input
- Provide channel metadata
- Authenticate deployment context
- Pass structured input to runtime

Adapters must not contain Skill logic.

---

# 5. Isolation Rules

- Deployment context must not leak between customers.
- Configuration must be loaded per execution.
- Execution must be stateless outside event storage.

---

# 6. Failure Handling

On failure:

- Emit failure event
- Tag error category
- Allow Control Plane evaluation

Runtime does not perform escalation.

---

# 7. Extensibility

Runtime must support:

- New channel adapters
- New action types
- New Skill definitions
- OpenClaw or alternate execution backends

---

# 8. Invariants

1. Every execution emits events.
2. Runtime must remain channel-agnostic.
3. Skill logic must not bypass event emission.
4. Action dispatch must be explicit.

---

# 9. Status

Version: v1
Scope: Execution Contract Only

