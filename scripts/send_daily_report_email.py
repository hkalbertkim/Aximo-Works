#!/usr/bin/env python3
import argparse
import os
import re
import smtplib
import sys
from email.message import EmailMessage
from pathlib import Path


def default_subject(report_path: Path) -> str:
    m = re.search(r"(\d{4}-\d{2}-\d{2})", report_path.name)
    if m:
        return f"AXIMO Daily Report {m.group(1)}"
    return "AXIMO Daily Report"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", required=True, help="Path to markdown report file")
    parser.add_argument("--to", default="hkalbert71@gmail.com", help="Recipient email")
    parser.add_argument("--subject", help="Email subject")
    args = parser.parse_args()

    gmail_from = os.environ.get("GMAIL_FROM")
    gmail_app_password = os.environ.get("GMAIL_APP_PASSWORD")
    if not gmail_from or not gmail_app_password:
        print("ERROR: Missing required env vars: GMAIL_FROM and/or GMAIL_APP_PASSWORD.", file=sys.stderr)
        return 1

    report_path = Path(args.report)
    if not report_path.exists() or not report_path.is_file():
        print(f"ERROR: Report file not found: {report_path}", file=sys.stderr)
        return 1

    report_text = report_path.read_text(encoding="utf-8")
    subject = args.subject or default_subject(report_path)

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = gmail_from
    msg["To"] = args.to
    msg.set_content(report_text)
    msg.add_attachment(
        report_text.encode("utf-8"),
        maintype="text",
        subtype="markdown",
        filename=report_path.name,
    )

    try:
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as smtp:
            smtp.starttls()
            smtp.login(gmail_from, gmail_app_password)
            smtp.send_message(msg)
    except Exception as e:
        print(f"ERROR: Failed to send email: {e}", file=sys.stderr)
        return 1

    print(f"OK: sent report email to {args.to}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
