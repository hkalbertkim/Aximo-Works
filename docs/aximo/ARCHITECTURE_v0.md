# AXIMO Architecture v0 (Single Source of Truth)

## 1) Customer Problem (Non-negotiable)
- Core customer: SMB founders exhausted by daily people and operations issues.
- Users do not want setup or training; they want direct commands like "Do this" and "Why is this not working?"
- Why Notion/Monday-style adoption fails: users are forced to become system designers.

## 2) One-line Definition of AXIMO
- AXIMO is not an "AI SaaS" product; it is "AI employee leasing" (workforce infrastructure).

## 3) Positioning
- Notion/Monday/OpenClaw/Workgroup are tools users must configure.
- AXIMO behaves like an employee: users state intent, and the work structure is generated and executed.

## 4) System Philosophy (3-layer Interface)
- Create: Web UI with text, guided selectable UI, and optional diagram-style controls (ComfyUI-like).
- Operate: Messenger text first, then progressive Voice channels (call/meeting).
- Presence: Vivido Avatar is a Phase 3 "last-inch" interface.

## 5) Architecture Guardrails
- All outbound sends/scheduling/invoicing must be approval-based.
- Audit logging is mandatory for key decisions and actions.
- Company memory must be strongly isolated per tenant.
- Global insights can only use anonymized, policy-governed aggregation with explicit consent.

## 6) Core Components (Brain)
- Control Plane API
- Role Builder: compiles commerce options into internal skill bundles and settings.
- Skill Registry: supports OpenClaw skills plus AXIMO-native skill format.
- Deterministic Router + Approval Gate
- Memory Store
- Audit Log
- Channel Adapters: Web / Messenger / Voice / Avatar

## 7) Multi-Agent Operations (Internal Team, External Single Persona)
- Core Trio (fixed): Planner / Executor / Critic-Risk
- Dynamic Specialist (max 1, conditional): strategy/analysis/reporting only, no execution authority.
- Principle: Execution is deterministic; strategy is deliberative.

## 8) Representative Scenario: Deal Execution Role (1-8)
- 1) Email intake: incoming customer communication creates a work trigger.
- 2) Customer structuring (DB/KB): normalize profile, history, and constraints into memory.
- 3) Draft order/proposal: generate role-based draft artifacts.
- 4) Negotiation and revision: track versions and expose risk implications.
- 5) Strategy report: produce options, evidence, and risks for decision-making.
- 6) Approval: all external actions must pass founder approval.
- 7) Customer communication/meeting/invoice: execute only approved actions.
- 8) Post-action sync: write outcomes back to audit log and memory.

## 9) MVP-0 (This Week’s Minimum Scope)
- Web text command -> intent parsing -> Admin Employee output.
- Approval gate enforced: no outbound send/schedule without approval.
- Keep Linear Daily Brief auto-post/status updates as operational tooling.

## 10) Phase Roadmap
- Phase 1: Web Create + Messenger Operate (text)
- Phase 2: Voice Operate (call/meeting)
- Phase 3: Vivido Presence (Avatar)
