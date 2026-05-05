# DEVOS: Permea-lab

## Project Identity

- Project ID: `permea_lab`
- Project name: Permea-lab
- Repository: `placeholder://repositories/permea-lab`
- Local project path: `/Users/albertkim/02_PROJECTS/18_Permea-lab`
- Owner machine: `M3-2`
- Priority: high
- Status: warm
- Department focus: dev, docs_proposal, product

## Strategic Purpose

Permea-lab is an open-source drug delivery intelligence project positioned as "AlphaFold for Delivery." The goal is to build an open, reproducible delivery intelligence layer for programmable therapeutics and drug delivery research.

The strategic intent is to make delivery evidence easier to compare, reproduce, and communicate. Permea-lab should support reviewer confidence, public credibility, and practical research workflows through transparent artifacts, benchmark contracts, delivery taxonomy, and evidence-ladder governance.

## Current Architecture Assumption

Permea-lab may contain multiple repositories or components, including `permea-core` and `permea-signal-ml`. Aximo Control should treat the exact remote URLs as unresolved until they are confirmed and approved.

Current assumptions:

- The project should remain open-source oriented and reproducibility-first.
- Delivery intelligence should be organized around explicit evidence, benchmark artifacts, and reviewable contracts.
- Taxonomy, evidence ladder, and benchmark contract conventions should guide how research claims are framed.
- Reviewer-facing materials should be structured, concise, and traceable to public or reproducible artifacts.
- Public credibility depends on clear governance, transparent limitations, and repeatable validation steps.

## Execution / Research Model

Typical work paths:

1. Organize delivery taxonomy and evidence ladder assumptions.
2. Define benchmark contracts and expected artifact formats.
3. Prepare reviewer packet materials and supporting evidence.
4. Track review feedback in a structured log.
5. Build reproducibility docs and public readiness checklists.
6. Maintain outreach templates for credible research and open-source engagement.

Each work item should leave a clear artifact: a document, benchmark output, evidence table, reproducibility note, or feedback log entry.

## Key Metrics

- Reviewer packet completeness
- Benchmark artifact completeness
- Reproducibility checklist coverage
- Evidence ladder coverage
- Delivery taxonomy coverage
- Public documentation readiness
- Review feedback closure rate
- Outreach template readiness

## Current Operating Focus

- Reviewer packet.
- Review feedback log.
- Outreach templates.
- Benchmark/evidence package.
- Reproducibility and public readiness.
- Delivery taxonomy / evidence ladder / benchmark contract style governance.

## Development Protocol

- Keep research claims traceable to evidence or clearly marked as assumptions.
- Prefer open, reproducible artifacts over opaque summaries.
- Keep benchmark contracts explicit and reviewable.
- Update status, task lists, or reports after meaningful changes.
- Preserve placeholder repository metadata until exact non-sensitive remote URLs are confirmed.
- Avoid adding private data, sensitive infrastructure details, or unpublished confidential claims.

## Approval Boundaries

- Do not add secrets, credentials, private tokens, customer data, or sensitive infrastructure details.
- Do not publish, push, open pull requests, merge, release, or change repository settings without explicit human approval.
- Public-facing, reviewer-facing, investor-facing, partner-facing, or customer-facing outputs require human approval.
- External outreach messages require human approval before sending.
- Exact GitHub URLs should not be invented; use placeholders until approved.

## Known Validation / Review Artifacts

- Reviewer packet.
- Review feedback log.
- Outreach templates.
- Benchmark/evidence package.
- Reproducibility documentation.
- Delivery taxonomy.
- Evidence ladder.
- Benchmark contract conventions.

No fresh Permea-lab validation run has been recorded in this control folder yet.

## Near-Term Milestones

| Milestone | Department | Status | Next Action |
| --- | --- | --- | --- |
| Reviewer packet baseline | docs_proposal | queued | Identify current packet structure and missing sections. |
| Review feedback log | docs_proposal, product | queued | Create or verify structured feedback tracking. |
| Benchmark/evidence package | dev | queued | Register current benchmark artifacts and reproducibility expectations. |
| Reproducibility docs pass | dev, docs_proposal | queued | Review setup, data, benchmark, and result reproduction notes. |
| Public credibility package | product, docs_proposal | queued | Align taxonomy, evidence ladder, and benchmark contract narrative. |
| DEVOS operating loop | dev, docs_proposal, product | active | Keep STATUS and TASKS aligned with Permea-lab work. |

## Risks / Unknowns

- Exact remote repositories and branch policies are not recorded in this control plane yet.
- Component boundaries between `permea-core`, `permea-signal-ml`, and any other local folders need confirmation.
- Benchmark claims may require careful qualification before public or reviewer-facing use.
- Reproducibility may depend on datasets, environments, or assumptions not yet registered here.
- Outreach and reviewer materials require human review before external use.

## Handoff Rules

- Start with `STATUS.md` for current state and `TASKS.md` for the active queue.
- Confirm local component structure before updating remote metadata.
- Tie claims to reproducible artifacts or label them as assumptions.
- Record validation commands, artifact checks, and review outcomes in project reports when meaningful work is completed.
- Keep sensitive details and private credentials out of this repo.
- Escalate blockers clearly instead of expanding research scope silently.
