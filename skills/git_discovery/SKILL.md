# Git Discovery Skill

## Purpose

Inspect local git repository state without modifying files.

## When To Use

- Starting a task.
- Preparing a discovery report.
- Checking machine or project status.
- Reviewing before commit or push.

## Read-Only Commands

```bash
pwd
git status --short
git status --short --branch
git branch --show-current
git log -5 --oneline
git remote -v
git rev-parse --show-toplevel
```

## Rules

- Do not run cleanup, restore, reset, checkout, merge, rebase, commit, or push commands unless explicitly requested.
- Treat dirty working trees as warnings.
- Preserve user and agent changes.
- Record path, branch, latest commit, remotes, and working tree status.

