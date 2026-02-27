# AXIMO WORKS — DOMAIN_MODEL_v1

## 1. Purpose

This document defines the Domain Model of Aximo Works using DDD principles.

Aximo Works is not a chatbot product.
It is a Skill-Based AI Workforce Runtime with a Founder-Controlled Execution Layer.

The purpose of this document is to:

- Establish a shared language (Ubiquitous Language)
- Define core domain concepts
- Identify bounded contexts
- Clarify aggregates and entity relationships

---

# 2. Ubiquitous Language

The following terms have strict meanings inside Aximo.

## 2.1 Skill

A reusable AI employee template.
A Skill defines logic, inputs, outputs, and allowed actions.

Examples:
- LeadCaptureSkill
- MeetingAgentSkill
- DevPMSkill
- DocumentDraftSkill

A Skill is versioned and immutable once published.

---

## 2.2 Deployment

An instance of a Skill installed for a specific Customer.

A Deployment binds:
- Skill Version
- Customer ID
- Configuration
- Channel(s)

Deployment is the unit of execution.

---

## 2.3 Configuration (Value Object)

Customer-specific settings applied to a Deployment.

Examples:
- Knowledge sources
- Routing rules
- Capture fields
- Tone
- Delivery targets

Configuration has no identity outside its Deployment.

---

## 2.4 Execution

A single runtime invocation of a Skill.

Execution includes:
- Input
- Context
- Skill logic
- Action dispatch
- Event emission

Each Execution produces structured events.

---

## 2.5 Action

A real-world effect produced by a Skill.

Examples:
- Send email
- Store lead in sheet
- Create task
- Update CRM
- Generate document

Actions may require approval depending on risk.

---

## 2.6 Event

A structured record of something that happened.

Examples:
- skill_executed
- lead_captured
- approval_requested
- approval_granted
- execution_failed

Events are immutable.

---

## 2.7 Control Plane

The governance layer supervising execution.

Responsibilities:
- Approval decisions
- SLA monitoring
- Escalation
- Pressure triggering

The Control Plane does not execute business logic.
It supervises it.

---

## 2.8 Channel Adapter

Interface between external input systems and the runtime.

Examples:
- Web widget
- Telegram bot
- Meeting transcript ingestion

Channel Adapters normalize input into execution format.

---

# 3. Bounded Contexts

Aximo consists of four primary bounded contexts.

---

## 3.1 Skill Factory Context

Responsible for:
- Skill definition
- Versioning
- Publishing
- Registry management

Core Entity:
- Skill

---

## 3.2 Runtime Context

Responsible for:
- Execution lifecycle
- Context building
- Action dispatch
- Channel handling

Core Aggregate:
- Deployment

Deployment is the execution root.

---

## 3.3 Control Context

Responsible for:
- Approval policies
- Risk evaluation
- SLA tracking
- Escalation logic

Core Aggregate:
- Execution Review

---

## 3.4 Audit Context

Responsible for:
- Event persistence
- Execution traceability
- Historical replay
- Metrics derivation

Core Entity:
- Event

Events are append-only.

---

# 4. Core Aggregates

## 4.1 Skill (Aggregate Root)

Owns:
- Version
- Metadata
- Risk classification

Does not own Deployments.

---

## 4.2 Deployment (Aggregate Root)

Owns:
- Configuration
- Active state
- Execution history reference

All runtime execution happens through Deployment.

---

## 4.3 Execution (Entity)

Child of Deployment.

Represents one invocation instance.

---

## 4.4 Event (Entity)

Global append-only log entry.

Linked to:
- Deployment
- Execution

---

# 5. Invariants

The following must always hold true:

1. A published Skill cannot change.
2. A Deployment references exactly one Skill version.
3. Every Execution emits at least one Event.
4. Events are immutable.
5. Suspension of a Deployment does not delete Events.

---

# 6. Relationship to Lifecycle Spec

Lifecycle defines states.
Domain Model defines structural ownership and boundaries.

Skill Lifecycle governs:
- State transitions
- Version movement
- Activation and suspension

Domain Model governs:
- Ownership
- Aggregates
- Invariants

---

# 7. Status

Version: v1
Scope: Core Domain Definition

This document establishes shared language and structural domain boundaries.
Further policy specifications extend this model.
