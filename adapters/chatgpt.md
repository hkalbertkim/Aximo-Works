# ChatGPT Adapter

## Purpose

Describe how ChatGPT should operate within Aximo workflows without making Aximo Control depend on ChatGPT.

## Usage Boundary

- Use ChatGPT for planning, report drafting, task packet creation, and reasoning-heavy review.
- Use explicit local file paths and task packets to preserve context.
- Treat generated text as draft operating material until reviewed.

## Constraints

- Do not assume persistent hidden context.
- Do not send secrets, credentials, customer data, or sensitive infrastructure details.
- Do not claim local validation unless a connected local tool actually ran it.
- Do not publish or send external messages without approval.

## Expected Handoff

ChatGPT output should map to Aximo commands, agents, skills, and reports so another adapter can continue the work.

