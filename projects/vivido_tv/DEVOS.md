# DEVOS: Vivido_TV

## Project Identity

- Project ID: `vivido_tv`
- Project name: Vivido_TV
- Repository: `placeholder://repositories/vivido-tv`
- Local project path: `/Users/albertkim/02_PROJECTS/04_vivido`
- Owner machine: `M1`
- Priority: high
- Status: active
- Department focus: dev, product, marketing, operations

## Strategic Purpose

Vivido_TV is a real-time AI persona and interactive video avatar project. The current direction is B2B-first, focused on multilingual customer avatars for museums, transport kiosks, visitor experiences, and public-facing service environments.

The near-term goal is beta readiness for `beta.vivido.tv`: a reliable deployment workflow, a usable Japanese beta tester flow, and a demonstrable real-time persona loop. The long-term direction may include creator and persona marketplace potential, but current operations should stay focused on beta execution and public-service reliability.

## Current Architecture Assumption

Vivido_TV may contain multiple components, including a sub-repo or component such as `web-next`. Aximo Control should treat exact remote URLs as unresolved until they are confirmed and approved.

Current assumptions:

- The primary product surface is an interactive, real-time persona experience.
- The beta flow should support multilingual scenarios, with current emphasis on Japanese beta testing.
- The avatar loop should expose clear listening, thinking, speaking, and reacting states.
- Operator/debug reporting should make failures, latency, and user-flow issues visible.
- Deployment work should be documented through a runbook before public beta use.

## Interaction Model

Typical persona loop:

1. Visitor or beta tester starts an interaction.
2. System enters a listening state and captures input.
3. System transitions to thinking while processing intent and persona response.
4. System enters speaking while delivering avatar output.
5. System reacts through visible or logged state changes.
6. Operator/debug reporting captures latency, errors, state transitions, and notable failures.

The interaction loop should be clear enough for both end users and operators. Beta validation should prove that the persona state model is understandable, recoverable, and measurable.

## Key Metrics

- Beta flow completion rate
- First-response latency
- End-to-end interaction latency
- Listening/thinking/speaking/reacting state accuracy
- Session error rate
- Deployment success rate
- Japanese beta tester completion rate
- Operator/debug report completeness
- Persona recovery rate after failed or interrupted interactions

## Current Operating Focus

- Beta readiness.
- `beta.vivido.tv` domain/deployment workflow.
- Japanese beta tester flow.
- Real-time persona loop.
- Listening / thinking / speaking / reacting state model.
- Operator/debug reporting.
- Deployment runbook and beta guide.

## Development Protocol

- Keep beta work small, testable, and report-driven.
- Validate deployment and domain changes through an explicit runbook.
- Track persona loop state behavior before claiming beta readiness.
- Update status, tasks, and reports after meaningful validation.
- Preserve placeholder repository metadata until exact non-sensitive remote URLs are confirmed.
- Do not include private credentials, customer data, or sensitive infrastructure details.

## Approval Boundaries

- Do not add secrets, credentials, private tokens, customer data, or sensitive infrastructure details.
- Do not publish, deploy, push, open pull requests, merge, release, or change repository settings without explicit human approval.
- Public-facing, customer-facing, partner-facing, or investor-facing outputs require human approval.
- Domain, DNS, deployment, production, or beta-public changes require explicit human approval.
- External beta communications require human approval before sending.
- Exact GitHub URLs should not be invented; use placeholders until approved.

## Known Validation / Beta Artifacts

- Beta deployment runbook.
- Beta guide.
- Japanese beta tester flow.
- Operator/debug report.
- Persona state model notes.
- Domain/deployment workflow notes for `beta.vivido.tv`.
- Real-time interaction validation checklist.

No fresh Vivido_TV beta validation run has been recorded in this control folder yet.

## Near-Term Milestones

| Milestone | Department | Status | Next Action |
| --- | --- | --- | --- |
| Beta deployment runbook | dev, operations | queued | Identify current deployment workflow and missing steps. |
| Japanese beta tester flow | product, marketing | queued | Define tester path, prompts, expected outcomes, and feedback capture. |
| Persona state model validation | dev, product | queued | Confirm listening, thinking, speaking, and reacting state behavior. |
| Operator/debug reporting baseline | dev, operations | queued | Define minimum report fields for beta diagnosis. |
| Beta guide | product, marketing | queued | Draft user-facing beta guide for approved review. |
| DEVOS operating loop | dev, product, marketing, operations | active | Keep STATUS and TASKS aligned with Vivido_TV beta work. |

## Risks / Unknowns

- Exact remote repositories and branch policies are not recorded in this control plane yet.
- Component boundaries, including any `web-next` sub-repo, need confirmation.
- Domain and deployment workflow may depend on external service configuration not stored here.
- Real-time persona quality depends on latency, state clarity, recovery behavior, and beta tester expectations.
- Public-facing beta materials and deployment changes require human review before use.

## Handoff Rules

- Start with `STATUS.md` for current state and `TASKS.md` for the active queue.
- Confirm local component structure before updating remote metadata.
- Treat domain, deployment, and public beta actions as approval-gated.
- Record validation commands, beta findings, operator reports, and deployment outcomes in project reports when meaningful work is completed.
- Keep sensitive details and private credentials out of this repo.
- Escalate blockers clearly instead of expanding beta scope silently.
