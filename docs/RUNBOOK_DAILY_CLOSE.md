# RUNBOOK: Daily Close ("오늘 정리하자")

## 트리거 문구
- `오늘 정리하자`

## 사전 조건 (Preconditions)
- 현재 작업 루트가 아래 경로여야 함:
  - `~/02_PROJECTS/03_aximo`
- 이메일 발송용 환경변수가 설정되어 있어야 함:
  - `GMAIL_FROM`
  - `GMAIL_APP_PASSWORD`

## Codex 실행 프롬프트 (복붙용)
아래 블록을 Codex에 그대로 입력한다.

```text
You are in ~/02_PROJECTS/03_aximo.

Daily Close routine for today (use system date in local timezone).
Execute in this exact order:

1) Generate today's human-readable report markdown:
   - Create docs/reports/AXIMO_DAILY_<YYYY-MM-DD>.md
   - Include these sections in Korean (concise):
     - What we built today (bullet list)
     - Proof/evidence summary (curl/test/proof snippets summarized)
     - Files changed / touched
     - Known issues/warnings
     - Next actions for tomorrow

2) Post Linear END comment to HKA-38 using existing script:
   - Command style:
     python3 scripts/post_daily_brief_to_linear.py --issue HKA-38 --text '<TEXT>'
   - Rule:
     - If an END comment for today already exists, post an ADDENDUM instead.
     - Otherwise post END for today.

3) Send the report email:
   - Command:
     python3 scripts/send_daily_report_email.py --report docs/reports/AXIMO_DAILY_<YYYY-MM-DD>.md

4) Git commit + push (optional, guarded):
   - Only if there are tracked changes.
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

## 출력 계약 (요약)
- Codex는 반드시 아래만 반환해야 함:
  - 실행한 정확한 명령어
  - Linear 코멘트 성공 라인
  - 이메일 발송 성공 라인
  - Git 결과 핵심 라인(또는 변경 없음)
- 비밀값/토큰/패스워드는 출력 금지
