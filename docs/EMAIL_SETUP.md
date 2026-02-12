# Email Setup (Gmail)

## Requirements
- Gmail account with 2-Step Verification enabled.
- Gmail App Password (required for SMTP login).

## Local Environment Variables
Set these in your local shell before running scripts:

```bash
export GMAIL_FROM="your_gmail_address@gmail.com"
export GMAIL_APP_PASSWORD="your_16_char_app_password"
```

You can also load these from a local env file such as `.env.local` (ignored by git).

## Send Daily Report

```bash
python3 scripts/send_daily_report_email.py --report docs/reports/AXIMO_DAILY_YYYY-MM-DD.md
```

Optional arguments:
- `--to` (default: `hkalbert71@gmail.com`)
- `--subject` (default derived from report filename)

## Security Note
- Never commit secrets to git.
- Keep credentials only in local environment variables or local env files (ignored).
