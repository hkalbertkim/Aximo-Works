# DEVOS: KORA

## Project Identity

- Project ID: `kora`
- Project name: KORA
- Repository: `placeholder://repositories/kora`
- Owner machine: `M3-1`
- Priority: high
- Status: active
- Department focus: dev, product, docs_proposal

## Strategic Purpose

KORA is the execution-layer architecture for Krako's near-term AI infrastructure. It is an inference-first execution and control layer designed to reduce unnecessary LLM and GPU invocation by routing work through cheaper execution paths whenever deterministic or lower-cost execution can satisfy the task.

The strategic goal is measurable AI execution efficiency: better task throughput per unit of energy and cost, with clear telemetry proving when KORA avoids expensive model calls without degrading expected outcomes.

## Current Architecture Assumption

KORA should operate as a deterministic-first control layer before expensive inference. The system should classify work, select the cheapest acceptable execution path, measure the result, and escalate only when lower-cost paths cannot satisfy the task.

Current assumptions:

- Deterministic rules and cache lookups should run before model inference.
- Small/local models should be preferred before GPU/LLM execution when quality requirements allow it.
- GPU/LLM execution should be treated as the expensive fallback path, not the default path.
- Every execution path should emit telemetry sufficient for cost, latency, and energy analysis.
- CLI workflows should remain stable enough to support repeatable smoke tests and public alpha validation.

## Execution Model

Typical execution paths:

1. Cache hit or previous result reuse.
2. CPU deterministic rules.
3. Small model or specialized lightweight model.
4. NPU/local model execution.
5. GPU/LLM execution only when necessary.

The routing layer should make escalation decisions explicit and auditable. Each task should record why a path was selected, what fallback occurred if any, and whether the result avoided unnecessary LLM/GPU invocation.

## Key Metrics

- Wh/task
- AI tasks/kWh
- GPU active energy
- Latency
- Cost/task
- Cache hit rate
- Deterministic resolution rate
- LLM invocation avoidance

## Current Operating Focus

- CLI hardening.
- Telemetry report generation.
- Public alpha readiness.
- KORA-DC Optimizer proposal/investor readiness.
- DEVOS-based repeatable project operations.

## Development Protocol

- Keep changes small, testable, and report-driven.
- Prefer deterministic behavior and clear execution traces over opaque automation.
- Validate CLI workflows before marking operational tasks done.
- Update project reports or status notes after meaningful changes.
- Preserve the placeholder repository reference until a non-sensitive exact repository URL is approved.

## Approval Boundaries

- Do not add secrets, credentials, private tokens, or sensitive infrastructure details.
- Do not publish, deploy, push, open pull requests, merge, or change repository settings without explicit human approval.
- Public-facing, investor-facing, partner-facing, or customer-facing outputs require human approval.
- Any external service connection or notification integration requires explicit approval.

## Known Smoke Tests

```bash
python3 -m kora --help
python3 -m kora examples list
python3 -m kora run hello_kora
python3 -m kora run retry_demo
python3 -m kora run direct_vs_kora -- --offline
python3 -m kora telemetry --input docs/reports/sample_telemetry_input.json
```

## Near-Term Milestones

| Milestone | Department | Status | Next Action |
| --- | --- | --- | --- |
| CLI hardening pass | dev | queued | Review known smoke tests and capture failures. |
| Telemetry report baseline | dev | queued | Confirm sample telemetry input and expected generated output. |
| Public alpha readiness checklist | product | queued | Define minimum public alpha acceptance criteria. |
| KORA-DC Optimizer proposal package | docs_proposal | queued | Draft investor-ready architecture and efficiency narrative. |
| DEVOS operating loop | dev, product, docs_proposal | active | Keep STATUS and TASKS aligned with current KORA work. |

## Risks / Unknowns

- Exact KORA repository URL is not recorded in this control plane yet.
- Energy measurement methodology may need hardware-specific calibration.
- Public alpha readiness depends on CLI reliability, docs clarity, and telemetry credibility.
- LLM invocation avoidance must be measured carefully to avoid overstating efficiency claims.
- Proposal/investor materials require human review before external use.

## Handoff Rules

- Start with `STATUS.md` for current state and `TASKS.md` for the active queue.
- Run or reference the known smoke tests before claiming CLI readiness.
- Record validation commands and outcomes in project reports when meaningful work is completed.
- Keep all sensitive details out of this repo.
- Escalate blockers clearly instead of expanding architecture scope silently.
