#!/usr/bin/env python3
"""Generate daily brief text and send it as an email report via SMTP."""

from __future__ import annotations

import os
import smtplib
import subprocess
import sys
from datetime import datetime
from email.message import EmailMessage

REQUIRED_SMTP_ENV = [
    "SMTP_HOST",
    "SMTP_PORT",
    "SMTP_USER",
    "SMTP_PASS",
    "EMAIL_FROM",
    "EMAIL_TO",
]


def _is_dry_run() -> bool:
    return os.getenv("DRY_RUN", "0") == "1"


def _missing_env(names: list[str]) -> list[str]:
    return [name for name in names if not os.getenv(name)]


def _run_daily_brief() -> str:
    proc = subprocess.run(
        ["python3", "daily_brief.py"],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"daily_brief.py failed: {proc.stderr.strip()}")
    return proc.stdout.strip()


def _send_email(brief_text: str) -> None:
    host = os.environ["SMTP_HOST"]
    port = int(os.environ["SMTP_PORT"])
    user = os.environ["SMTP_USER"]
    password = os.environ["SMTP_PASS"]
    from_addr = os.environ["EMAIL_FROM"]
    to_addr = os.environ["EMAIL_TO"]

    msg = EmailMessage()
    msg["Subject"] = f"AXIMO EOD Report - {datetime.now().strftime('%Y-%m-%d')}"
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg.set_content(brief_text)

    with smtplib.SMTP(host, port, timeout=30) as server:
        server.starttls()
        server.login(user, password)
        server.send_message(msg)


def main() -> int:
    dry_run = _is_dry_run()
    missing = _missing_env(REQUIRED_SMTP_ENV)

    if missing:
        names = ", ".join(missing)
        if dry_run:
            print(f"DRY_RUN: missing SMTP env vars: {names}")
            print("DRY_RUN: would run daily_brief.py and send email if env vars were set")
            return 0
        print(f"ERROR: missing SMTP env vars: {names}", file=sys.stderr)
        return 1

    if dry_run:
        print("DRY_RUN: would run daily_brief.py")
        print("DRY_RUN: would send email using env vars: SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, EMAIL_FROM, EMAIL_TO")
        return 0

    try:
        brief = _run_daily_brief()
        _send_email(brief)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print("Sent EOD email report")
    return 0


if __name__ == "__main__":
    sys.exit(main())
