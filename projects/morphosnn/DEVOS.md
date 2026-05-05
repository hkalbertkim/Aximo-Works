# DEVOS: MorphoSNN

## Project Identity

- Project ID: `morphosnn`
- Project name: MorphoSNN
- Repository: `placeholder://repositories/morphosnn`
- Local project path: `/Users/albertkim/02_PROJECTS/21_MorphoSNN`
- Owner machine: `M3-1`
- Priority: medium
- Status: research
- Department focus: dev, docs_proposal, product

## Strategic Purpose

MorphoSNN is a bio-inspired neuromorphic control project for deformable manufacturing and adaptive robotics. It explores how insect-inspired distributed control, local SNN/CPG controllers, body graph representation, and global coordination can handle non-rigid materials and embodied control problems.

The strategic goal is to produce a proposal-ready and technically credible control architecture for irregular manufacturing domains such as leather, fabric, film, cable, soft robotics, and other non-rigid or hard-to-model processes.

## Current Architecture Assumption

MorphoSNN should treat morphology, contact, and deformation as first-class control inputs instead of forcing all behavior into a single centralized controller. The architecture should combine local fast control with global coordination and explicit body graph structure.

Current assumptions:

- A Body Graph should represent parts, contact points, sensors, actuators, and deformable relationships.
- Local SNN/CPG Controllers should handle fast rhythmic, reactive, or local adaptation behavior.
- A Global Coordination Network should supervise goals, constraints, and cross-body synchronization.
- Benchmarks should reflect deformable material handling and adaptive robotics tasks, not only abstract control demos.
- Proposal materials should separate validated claims from hypotheses and open research questions.

## Control / Research Model

Typical control and research flow:

1. Define a Body Graph for the target morphology or material process.
2. Assign local SNN/CPG controllers to relevant nodes, segments, or contact regions.
3. Use global coordination to align local behaviors with task-level goals.
4. Measure stability, adaptation, recovery, material handling quality, and control efficiency.
5. Record benchmark outcomes and failure modes.
6. Convert validated findings into proposal-ready technical framing.

The research model should keep architecture, benchmark design, and proposal claims tightly linked.

## Key Metrics

- Control stability
- Adaptation time
- Recovery rate after perturbation
- Material handling success rate
- Deformation tracking quality
- Local controller response latency
- Global coordination convergence
- Benchmark reproducibility
- Proposal artifact completeness

## Current Operating Focus

- Bio-inspired neuromorphic control architecture.
- Research organization.
- Proposal-ready technical framing.
- Body Graph.
- Local SNN/CPG Controllers.
- Global Coordination Network.
- Benchmark and validation structure.
- Public/open-core technical package readiness.

## Development Protocol

- Keep research claims traceable to simulations, benchmarks, literature, or clearly marked hypotheses.
- Separate architecture notes, benchmark artifacts, and proposal framing.
- Prefer small validation artifacts over broad unverified claims.
- Update status, tasks, or reports after meaningful research organization or validation work.
- Preserve placeholder repository metadata until exact non-sensitive remote URLs are confirmed.
- Do not include unpublished partner details, private credentials, customer data, or sensitive infrastructure details.

## Approval Boundaries

- Do not add secrets, credentials, private tokens, customer data, unpublished partner details, or sensitive infrastructure details.
- Do not publish, push, open pull requests, merge, release, or change repository settings without explicit human approval.
- Public-facing, open-core, investor-facing, partner-facing, or customer-facing outputs require human approval.
- External proposal materials require human approval before use.
- Exact GitHub URLs should not be invented; use placeholders until approved.

## Known Validation / Research Artifacts

- Body Graph notes.
- Local SNN/CPG Controller notes.
- Global Coordination Network notes.
- Benchmark and validation structure.
- Research organization map.
- Proposal-ready technical framing.
- Public/open-core technical package checklist.

No fresh MorphoSNN validation run has been recorded in this control folder yet.

## Near-Term Milestones

| Milestone | Department | Status | Next Action |
| --- | --- | --- | --- |
| Architecture map | dev, docs_proposal | queued | Draft Body Graph, local controller, and global coordination boundaries. |
| Research organization pass | docs_proposal | queued | Inventory notes, claims, hypotheses, and missing references. |
| Benchmark structure | dev | queued | Define initial deformable material and adaptive robotics validation tasks. |
| Proposal technical framing | docs_proposal, product | queued | Convert architecture into proposal-ready narrative with clear claims. |
| Open-core package readiness | product, dev | queued | Define what can be public, what remains research, and what needs approval. |
| DEVOS operating loop | dev, docs_proposal, product | active | Keep STATUS and TASKS aligned with MorphoSNN research work. |

## Risks / Unknowns

- Exact remote repository and branch policy are not recorded in this control plane yet.
- Benchmark environments and target tasks need confirmation.
- Some claims may be hypotheses until supported by simulation, prototype, or literature references.
- Public/open-core packaging may require careful review to avoid overclaiming or exposing sensitive collaboration context.
- Hardware or robotics validation may depend on environments not registered in this repo.

## Handoff Rules

- Start with `STATUS.md` for current state and `TASKS.md` for the active queue.
- Confirm local component structure before updating remote metadata.
- Keep Body Graph, local SNN/CPG Controllers, Global Coordination Network, benchmarks, and proposal framing aligned.
- Record validation commands, research findings, artifact checks, and open questions in project reports when meaningful work is completed.
- Keep sensitive details, unpublished partner details, and private credentials out of this repo.
- Escalate blockers clearly instead of expanding research scope silently.
