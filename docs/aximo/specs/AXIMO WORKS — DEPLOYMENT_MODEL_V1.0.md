# AXIMO WORKS — DEPLOYMENT_MODEL_v1

## 1. Purpose

This document defines the deployment model of Aximo Works.

Aximo must support:

- DFY delivery in early stage
- SaaS-ready architecture in long term

Therefore, the system must be multi-tenant capable internally, while allowing DFY onboarding externally.

---

# 2. Key Definitions

## 2.1 Customer (Tenant)

A Customer is a tenant boundary.
All data and execution context must be scoped by Customer.

Customer attributes (minimum):

- customer_id
- name
- contact
- status

---

## 2.2 Deployment

A Deployment is an installed instance of a Skill for a Customer.

Deployment binds:

- customer_id
- skill_id
- skill_version
- configuration
- channel bindings
- status

Deployment is the unit of execution and operational management.

---

# 3. Tenancy Model

## 3.1 Early Stage Delivery (DFY)

- Operator performs installation and configuration.
- Customer does not need dashboard access.
- Deployment is created and activated by operator.

DFY onboarding steps (conceptual):

1. Collect customer inputs
2. Create customer record
3. Select skill + version
4. Generate configuration
5. Bind channels
6. Validate configuration
7. Activate deployment

---

## 3.2 SaaS-Ready Internal Structure

Even during DFY, the system must behave as multi-tenant:

- Every database record is scoped by customer_id
- Every execution loads config by customer_id + deployment_id
- Every event is written with customer_id

SaaS UI can later be layered without restructuring core data.

---

# 4. Data Isolation Rules

Aximo must ensure:

1. No cross-customer configuration reads
2. No cross-customer event reads
3. No cross-customer execution memory
4. Customer-scoped metrics

Isolation strategies:

- Logical isolation (customer_id scoping)
- Optional physical isolation (separate DB per customer) for high-security clients

Initial default: logical isolation.

---

# 5. Configuration Storage

Configuration is stored per Deployment.

Configuration includes:

- Knowledge sources
- Routing rules
- Capture fields
- Delivery targets
- Guardrails
- Tone

Configuration must be validated before activation.

---

# 6. Channel Binding

A Deployment may bind to one or more channels.

Examples:

- Web widget
- Telegram bot
- Meeting transcript ingestion

Channel binding must include:

- Channel type
- Connection details
- Authentication / secrets
- Enable/disable status

Channel adapters must always resolve deployment_id + customer_id.

---

# 7. Version Upgrade & Rollback

## 7.1 Version Upgrade

- Deployments pin a specific skill_version.
- Upgrading requires explicit operator or customer action.
- Upgrade may require config migration.

Upgrade flow:

1. Select target version
2. Validate compatibility
3. Migrate configuration (if needed)
4. Activate new version
5. Monitor

---

## 7.2 Rollback

Rollback must be supported.

Rollback requirements:

- Previous version remains installable for rollback
- Event log continuity preserved
- Deployment history records version changes

---

# 8. Observability Hooks

Deployments must expose:

- status
- last execution timestamp
- error rate
- SLA violations

These are used by Control Plane for governance.

---

# 9. Billing Hooks (Future)

Billing is not implemented in v1.

However, deployment model must allow later billing by:

- per deployment
- per action
- per execution
- per event volume

Therefore, executions and actions must be countable and attributable to customer_id.

---

# 10. Invariants

1. Every deployment belongs to exactly one customer.
2. Every execution belongs to exactly one deployment.
3. Every event is scoped to customer_id.
4. Skill versions are pinned per deployment.
5. Upgrades and rollbacks must be auditable.

---

# 11. Status

Version: v1
Scope: Deployment + Tenancy Model

