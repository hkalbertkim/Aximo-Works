# AXIMO WORKS — SKILL_LIFECYCLE_SPEC_v1

## 1. Purpose

This document defines the lifecycle model of a Skill within Aximo Works.

A Skill is not a feature.
A Skill is an installable AI employee template.

The lifecycle governs:

- How a Skill is created
- How it is published
- How it is deployed
- How it executes
- How it is updated
- How it is suspended or deprecated

This document defines the canonical lifecycle states.

---

# 2. Skill Definition Model

Each Skill must include the following metadata:

- Skill ID
- Skill Name
- Version
- Description
- Supported Channels (Web, Telegram, Meeting, etc.)
- Supported Action Types
- Default Risk Level
- Default Approval Mode
- Guardrail Policy

A Skill is versioned and immutable once published.

---

# 3. Skill States

A Skill moves through the following states:

## 3.1 Draft

- Not installable
- Under development
- May change freely

## 3.2 Published

- Installable
- Version locked
- Cannot change logic without version increment

## 3.3 Installable

- Available for deployment
- Listed in Skill Registry

## 3.4 Deprecated

- No new installations allowed
- Existing deployments may continue running

---

# 4. Deployment Lifecycle

A Deployment represents a Skill installed for a specific Customer.

Each Deployment has its own state.

## 4.1 Pending Configuration

- Skill selected
- Configuration not complete

## 4.2 Configured

- Configuration validated
- Ready for activation

## 4.3 Active

- Skill running
- Accepting inputs

## 4.4 Suspended

- Temporarily disabled
- No execution triggered

## 4.5 Error

- Execution failures detected
- Requires manual review

## 4.6 Terminated

- Deployment removed
- Execution disabled permanently

---

# 5. Execution Lifecycle

Each execution instance follows this flow:

## 5.1 Triggered

Input received via channel adapter.

## 5.2 Processing

Context built and Skill logic executed.

## 5.3 Awaiting Approval (if required)

Execution paused until founder or operator approval.

## 5.4 Completed

Action dispatched successfully.

## 5.5 Failed

Execution error recorded.
Event emitted.

---

# 6. Versioning Model

- Every published Skill has a semantic version.
- Deployments reference a specific version.
- Version upgrades require explicit migration.
- Rollback must be supported.

Versioning ensures stability and audit traceability.

---

# 7. Risk & Approval Hook Points (Structural Only)

This document does not define risk levels.

However, the lifecycle must support:

- Risk evaluation before action dispatch
- Conditional approval requirement
- Execution pause before irreversible actions

Risk and approval logic are defined in CONTROL_PLANE_SPEC_v1.

---

# 8. Design Constraints

1. A Skill definition must be immutable once published.
2. Deployments must be isolated per customer.
3. Every execution must emit structured events.
4. Suspension must not delete historical data.
5. Version rollback must preserve audit trail.

---

# 9. Relationship to SYSTEM_MAP

Skill Lifecycle operates within:

Skill Registry → Deployment Manager → Agent Runtime → Event Log → Control Plane

Lifecycle defines state.
Runtime defines execution.
Control Plane defines governance.

---

# 10. Status

Version: v1
Scope: Lifecycle Definition Only

This document defines the structural lifecycle of Skills and Deployments.
Further policy definitions will extend this model.

