# AXIMO WORKS — SKILL_REGISTRY_SPEC_v1

## 1. Purpose

This document defines the Skill Registry.

The Skill Registry is the canonical catalog of all Skills.
It enables:

- Discoverability (what skills exist)
- Versioning (which versions are available)
- Compatibility checks
- Deployment selection
- Future marketplace extension

The registry is a factory component.
It is not customer-specific.

---

# 2. Registry Responsibilities

The Skill Registry must:

1. Store Skill metadata
2. Store Skill versions
3. Mark versions as installable or deprecated
4. Expose selection and filtering by channel/action
5. Provide compatibility metadata for upgrades

---

# 3. Skill Metadata Schema (Conceptual)

Each Skill entry must include:

- skill_id (stable identifier)
- name
- short_description
- long_description
- categories (lead, meeting, dev, docs, ops)
- supported_channels
- supported_action_types
- default_risk_level
- default_approval_mode
- guardrail_policy_id
- owner (internal/team/third-party)

---

# 4. Skill Version Schema (Conceptual)

Each Skill version must include:

- skill_id
- version (semantic version)
- published_at
- changelog
- installable (true/false)
- deprecated (true/false)
- compatibility
  - min_runtime_version
  - max_runtime_version (optional)
  - config_schema_version
- artifacts
  - runtime_entrypoint
  - prompt_templates
  - output_schema
  - test_suite_id

A published version is immutable.

---

# 5. Registry Operations

## 5.1 Create Skill (Draft)

- Create skill_id
- Register metadata
- Create initial draft version

## 5.2 Publish Version

- Freeze artifacts
- Write changelog
- Mark as installable

## 5.3 Deprecate Version

- Set deprecated=true
- installable=false
- Existing deployments may continue

## 5.4 Retire Skill

- All versions deprecated
- Skill hidden from default selection

---

# 6. Compatibility & Upgrade Support

The registry must support a compatibility model.

Purpose:

- Prevent invalid upgrades
- Support config migration

Minimum requirements:

- config_schema_version per skill version
- runtime compatibility bounds

Upgrade decision rule (conceptual):

- If target config_schema_version differs, migration is required.

---

# 7. Discovery & Filtering

The registry must allow queries such as:

- Skills supporting channel = Web
- Skills supporting action = send_email
- Skills in category = lead
- Skills requiring approval = REQUIRED

This enables:

- Operator DFY workflows
- Future self-serve selection

---

# 8. Testing Requirements

Each published Skill version must include:

- Minimal test suite
- Reference inputs
- Expected outputs

The registry stores linkage to the test suite.

A version cannot be marked installable without tests.

---

# 9. Future Marketplace Extension (Non-binding)

Registry must be designed to later support:

- Third-party owners
- Permissioning
- Monetization metadata
- Review/verification status

This is not implemented in v1.

---

# 10. Invariants

1. skill_id is stable across versions.
2. published versions are immutable.
3. installable versions must have tests.
4. deprecating does not remove historical deployments.

---

# 11. Status

Version: v1
Scope: Registry Specification

