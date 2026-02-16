# Email Setup (Gmail)

## Requirements
- A Gmail account with 2-Step Verification enabled.
- A Gmail App Password for SMTP login (regular account password will not work).

## Local Environment Variables
Set these variables in your local shell before running email scripts:

```bash
export GMAIL_FROM="your_gmail_address@gmail.com"
export GMAIL_APP_PASSWORD="your_16_char_app_password"
```

You may also load them from a local env file such as `.env.local` (git-ignored).

## Send Daily Report

```bash
python3 scripts/send_daily_report_email.py --report docs/reports/AXIMO_DAILY_YYYY-MM-DD.md
```

## Optional Arguments
- `--to` (default: `hkalbert71@gmail.com`)
- `--subject` (default derived from report filename)

## Security Notes
- Never commit secrets.
- Keep credentials only in local environment variables or local ignored files.
