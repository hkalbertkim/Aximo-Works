# Task Packet Creation Skill

## Purpose

Create a clear task packet that can be executed by a human or tool adapter without relying on hidden context.

## When To Use

- Starting a new implementation, validation, reporting, or operations task.
- Converting a follow-up action into an executable local task.
- Preparing work for another agent or future session.

## Required Fields

- Task ID or title.
- Project and department.
- Owner machine if known.
- Goal.
- Context.
- Allowed files or repositories.
- Explicit exclusions.
- Validation commands.
- Expected report or dashboard updates.

## Output

Write the task packet as Markdown or YAML, depending on the surrounding workflow. Keep it local, auditable, and free of secrets.

