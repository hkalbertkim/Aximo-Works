# Aximo-Works To Aximo Control Integration Plan

## 1. Goal

Create a safe, non-destructive plan for transitioning the existing remote `Aximo-Works` repository toward the Aximo Control operating scaffold.

The plan must preserve existing remote history and runtime/application files until a separate migration decision is approved. No force push, merge of unrelated histories, reset, file deletion, repository setting change, deployment, or external integration should occur as part of this planning step.

## 2. Current State

Local repository:

- Path: `/Users/albertkim/02_PROJECTS/03_aximo_os_control`
- Branch: `main`
- Remote: `https://github.com/hkalbertkim/Aximo-Works.git`
- Latest local commit: `d8fc226 Add Aximo operating scaffold`
- Status after fetch: `main` is ahead of `origin/main` by 22 commits and behind by 59 commits.

Remote repository:

- Repository: `https://github.com/hkalbertkim/Aximo-Works.git`
- Latest remote commit: `72ac1dd docs: upgrade README to Execution OS v1 and add Context Snapshot (2026-02-25)`
- Existing shape: execution-pressure/work-push application runtime with backend, frontend, operations scripts, Telegram/Linear automation, launchd plists, and runtime docs.

## 3. History Divergence Summary

The local Aximo Control repository and remote `Aximo-Works` repository have unrelated histories.

Observed relationship:

```text
main...origin/main: 22 local-only commits, 59 remote-only commits
```

`git diff origin/main...main` fails because there is no merge base:

```text
fatal: origin/main...main: no merge base
```

Implication:

- A normal fast-forward push is not possible.
- A normal comparison using triple-dot diff is not possible.
- Any direct integration requires an intentional branch strategy.
- Force push would overwrite the existing `Aximo-Works` history and must not be used without separate explicit approval.

## 4. Local Aximo Control Assets

Local Aximo Control assets that define the new operating scaffold:

- `AXIMO.md`
- `AGENTS.md`
- `README.md`
- `adapters/`
- `agents/`
- `commands/`
- `hooks/`
- `skills/`
- `config/`
- `dashboards/`
- `projects/`
- `reports/`
- `scripts/check_machine_status.py`
- `scripts/daily_close.py`
- `scripts/discover_projects.py`
- `scripts/generate_dashboard.py`
- `scripts/generate_task_dashboard.py`
- `scripts/move_task.py`
- `scripts/new_report.py`
- `scripts/new_task.py`
- `scripts/validate_config.py`
- `tasks/`
- `templates/`

These assets represent the Markdown/YAML/Python-first control-plane model and should be migrated onto a branch based on the remote repository if the transition proceeds.

## 5. Remote Aximo-Works Existing Assets

Remote `origin/main` currently includes an application/runtime structure:

- `.env.example`
- `.gitignore`
- `LICENSE`
- `README.md`
- `assets/`
- `aximo/`
- `aximo_cli.py`
- `backend/`
- `daily_brief.py`
- `docs/`
- `frontend/aximo-web/`
- `intake_from_clipboard.sh`
- `linear_bootstrap_aximo_engine.py`
- `linear_cli.py`
- `linear_routing.json`
- `llm_local_test.py`
- `ops/`
- `post_daily_brief.py`
- `requirements.txt`
- `run_ops.sh`
- `scripts/`
- `slack_live_test.py`

These files reflect the earlier execution-pressure/work-push direction and should be preserved initially.

## 6. Integration Risks

- Histories are unrelated, so careless merges can produce confusing repository history and large conflicts.
- Remote has real application/runtime content that may still be valuable as a historical or reusable execution layer.
- Local has a new control-plane model that may conflict conceptually with remote README and product positioning.
- Both local and remote have `README.md` and `scripts/`, so path-level conflicts are likely if copied directly.
- Remote contains operational scripts, launchd plists, Telegram-related files, Linear scripts, and frontend/backend application code. These should not be modified or removed until explicitly reviewed.
- Remote includes `scripts/__pycache__/...` paths, which should be reviewed later but not removed in this planning task.
- A force push from local `main` would replace the remote repository content and should be treated as destructive.

## 7. Recommended Strategy

Recommended default: add Aximo Control on top of existing `Aximo-Works` without overwriting remote history.

Steps:

1. Create a new branch from `origin/main`.
2. Copy or add the Aximo Control scaffold and file-based operating assets onto that branch.
3. Preserve existing remote runtime/application files initially.
4. Add transition documentation that explains the new Control-centered direction.
5. Keep the older execution-pressure app/runtime available for review.
6. Do not force push.
7. Do not delete or archive existing runtime files until a separate file-level migration plan is approved.

This strategy keeps remote history intact while allowing Aximo Control to become the forward operating layer.

## 8. Proposed Target Repository Structure

Initial non-destructive target structure on a new branch from `origin/main`:

```text
AXIMO.md
AGENTS.md
README.md                         # update later only after separate approval
adapters/
agents/
commands/
config/
dashboards/
hooks/
projects/
reports/
scripts/                          # add Aximo Control helpers carefully
skills/
tasks/
templates/

assets/                           # preserve from remote
aximo/                            # preserve from remote
backend/                          # preserve from remote
docs/                             # preserve from remote; add transition docs carefully
frontend/                         # preserve from remote
ops/                              # preserve from remote
```

If path conflicts arise, prefer one of these approaches:

- Add control-plane scripts under `scripts/control/`.
- Add transition docs under `docs/control/`.
- Keep existing remote runtime scripts unchanged until reviewed.

## 9. Files To Add From Local Control Scaffold

Recommended additions from local Aximo Control:

- `AXIMO.md`
- `AGENTS.md`
- `adapters/`
- `agents/`
- `commands/`
- `config/`
- `dashboards/`
- `hooks/`
- `projects/`
- `reports/daily/`
- `reports/machine/`
- `reports/plans/`
- `reports/project/`
- `reports/reviews/`
- `skills/`
- `tasks/`
- `templates/`

Recommended helper scripts to add, with conflict review:

- `scripts/check_machine_status.py`
- `scripts/daily_close.py`
- `scripts/discover_projects.py`
- `scripts/generate_dashboard.py`
- `scripts/generate_task_dashboard.py`
- `scripts/move_task.py`
- `scripts/new_report.py`
- `scripts/new_task.py`
- `scripts/validate_config.py`

Because remote already has a `scripts/` directory, script additions should be reviewed path-by-path before copying. If needed, place Aximo Control helpers under `scripts/control/` to avoid confusing them with existing runtime scripts.

## 10. Remote Files To Preserve Initially

Preserve these remote files/directories during the first integration branch:

- `LICENSE`
- `README.md`
- `assets/`
- `aximo/`
- `aximo_cli.py`
- `backend/`
- `docs/`
- `frontend/`
- `ops/`
- `requirements.txt`
- `run_ops.sh`
- Existing root scripts and automation files.

Reason: these files represent existing work and remote history. Their future role should be determined after the Control scaffold is safely added and reviewed.

## 11. Remote Files To Review For Archive Later

Review these later for archive, retention, or replacement:

- `backend/`
- `frontend/aximo-web/`
- `ops/launchd/`
- Telegram scripts.
- Linear scripts.
- Slack test script.
- Runtime smoke scripts.
- Existing daily report/email automation.
- Existing `docs/reports/` historical reports.
- Existing `docs/aximo/specs/` product/runtime specs.
- Existing `scripts/__pycache__/...` tracked bytecode paths.

Possible future archive path:

```text
archive/execution-pressure-v1/
```

No archive move should happen until explicitly approved.

## 12. Files Not To Touch Yet

Do not touch these categories in the initial integration:

- Remote application source under `backend/`, `frontend/`, and `aximo/`.
- Remote operational scripts under `ops/`.
- Remote launchd plist files.
- Remote Telegram, Linear, Slack, and email automation files.
- Remote `README.md` product positioning, unless a transition README edit is separately approved.
- Remote `LICENSE`.
- Any secrets, credentials, environment files, GitHub settings, branch protection, webhooks, actions, or integrations.

## 13. Proposed Branch Strategy

Recommended branch workflow:

```bash
git fetch origin
git switch -c transition/control-scaffold origin/main
```

Then copy selected Aximo Control files from the local control history or working copy into this branch.

Do not use:

- `git merge --allow-unrelated-histories` without a detailed conflict plan.
- `git rebase`.
- `git reset`.
- `git push --force`.

The branch should be reviewed locally before any push or PR.

## 14. Proposed Commit Strategy

Suggested commit sequence on the transition branch:

1. `Add Aximo Control operating scaffold`
   - Add `AXIMO.md`, adapters, agents, commands, hooks, skills.

2. `Add Aximo Control file-based state`
   - Add `config/`, `dashboards/`, `projects/`, `tasks/`, `templates/`.

3. `Add Aximo Control reporting helpers`
   - Add report/task/machine helper scripts in an agreed path.

4. `Add Aximo Control transition reports`
   - Add plans, reviews, and daily reports that explain the transition.

Keep each commit reviewable and non-destructive.

## 15. Validation Plan

Run these validations on the integration branch:

```bash
python3 scripts/validate_config.py
python3 scripts/generate_dashboard.py
python3 scripts/generate_task_dashboard.py
python3 scripts/check_machine_status.py
python3 scripts/daily_close.py
git status --short --branch
```

If helper scripts are moved under `scripts/control/`, update command paths accordingly.

Also run a secret/sensitive-content scan on newly added Control files before any commit or push.

## 16. Approval Gates

Require explicit human approval before:

- Pushing any transition branch.
- Opening a PR.
- Merging.
- Force pushing.
- Moving or archiving existing remote runtime files.
- Replacing remote `README.md`.
- Changing repository settings.
- Connecting external services.
- Adding dependencies.
- Deploying or running remote application operations.
- Sending external messages.

## 17. Recommended Next Task

Task 021 — Build Non-Destructive Transition Branch From `origin/main`

Suggested scope:

- Create a new branch from `origin/main`.
- Add only the Aximo Control scaffold files first.
- Avoid modifying remote runtime/application files.
- Run validation and secret scan.
- Produce a branch review report.
- Do not push until explicitly approved.

