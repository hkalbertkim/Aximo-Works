# RUNBOOK: Daily Close ("오늘 정리하자")

## Trigger Phrase
- `오늘 정리하자`

## Preconditions
- Repository root must be:
  - `~/02_PROJECTS/03_aximo`
- Required email environment variables must exist:
  - `GMAIL_FROM`
  - `GMAIL_APP_PASSWORD`

## Codex Prompt Template (Copy/Paste)
Use the prompt below in Codex exactly as written.

```text
You are in ~/02_PROJECTS/03_aximo.

Daily close routine for today (use local timezone date).
Execute in this exact order:

1) Generate today's human-readable report markdown:
   - Create docs/reports/AXIMO_DAILY_<YYYY-MM-DD>.md
   - Include these sections in concise English:
     - What we built today (bullet list)
     - Proof/evidence summary (curl/test/proof snippets summarized)
     - Files changed/touched
     - Known issues/warnings
     - Next actions for tomorrow

2) Post Linear END comment to HKA-38 using existing script:
   - Command pattern:
     python3 scripts/post_daily_brief_to_linear.py --issue HKA-38 --text '<TEXT>'
   - Rule:
     - If an END comment already exists for today, post an ADDENDUM.
     - Otherwise post END for today.

3) Send the report email:
   - Command:
     python3 scripts/send_daily_report_email.py --report docs/reports/AXIMO_DAILY_<YYYY-MM-DD>.md

4) Git commit + push (optional, guarded):
   - Execute only if there are tracked changes.
   - Commit message format:
     Daily close YYYY-MM-DD
   - Push target:
     main

Output contract (strict):
- Return ONLY:
  - exact commands run
  - success lines for Linear post
  - success line for email send
  - git status/commit/push key result lines (or explicit "no tracked changes")
- Do not print secrets.
```

## Output Contract (Summary)
- Codex must return only:
  - exact commands executed
  - Linear post success line
  - email send success line
  - Git key result lines (or no tracked changes)
- Never output secrets, tokens, or passwords.
