#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
LOG_PATH = ROOT / "logs" / "daily_close.out.log"


def ts() -> str:
    return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")


def log_line(message: str) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(f"[{ts()}] {message}\n")


def run_cmd(cmd: list[str], timeout: int = 30) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def sanitize_header_text(text: str) -> str:
    lines = []
    for line in text.splitlines():
        if line.lower().startswith("set-cookie:"):
            continue
        lines.append(line)
    return "\n".join(lines)


def first_http_status(header_text: str) -> str:
    for line in header_text.splitlines():
        if line.startswith("HTTP/"):
            return line.strip()
    return "(no status line)"


def check_http_head(url: str, expect_status: str) -> tuple[bool, str]:
    proc = run_cmd(["curl", "-I", "-s", url], timeout=30)
    merged = sanitize_header_text((proc.stdout or "") + "\n" + (proc.stderr or ""))
    status = first_http_status(merged)
    ok = proc.returncode == 0 and expect_status in status
    return ok, status


def check_backend_health() -> tuple[bool, str, bool]:
    proc = run_cmd(["curl", "-s", "http://127.0.0.1:8000/health"], timeout=30)
    body = (proc.stdout or "").strip()
    try:
        payload = json.loads(body)
        ok = bool(payload.get("ok") is True)
        return ok, body[:200], not ok
    except Exception:
        return False, body[:200] if body else "(invalid json)", True


def launchd_summary(labels: list[str]) -> list[str]:
    uid = run_cmd(["id", "-u"]).stdout.strip()
    out: list[str] = []
    for label in labels:
        proc = run_cmd(["launchctl", "print", f"gui/{uid}/{label}"], timeout=30)
        if proc.returncode != 0:
            out.append(f"{label}: FAIL launchctl")
            continue
        state = "(n/a)"
        pid = "(n/a)"
        last_exit = "(n/a)"
        active = "(n/a)"
        for raw in proc.stdout.splitlines():
            line = raw.strip()
            if line.startswith("state = ") and state == "(n/a)":
                state = line.split("=", 1)[1].strip()
            elif line.startswith("pid = ") and pid == "(n/a)":
                pid = line.split("=", 1)[1].strip()
            elif line.startswith("last exit code = ") and last_exit == "(n/a)":
                last_exit = line.split("=", 1)[1].strip()
            elif line.startswith("active count = ") and active == "(n/a)":
                active = line.split("=", 1)[1].strip()
        out.append(f"{label}: state={state} pid={pid} active={active} last_exit={last_exit}")
    return out


def main() -> int:
    lines: list[str] = []
    lines.append(f"timestamp={ts()}")
    lines.append(f"repo={ROOT}")

    critical_fail = False

    # 1) Quickcheck
    f_ok, f_status = check_http_head("http://127.0.0.1:3000", "200")
    lines.append(f"quickcheck.frontend_local={'PASS' if f_ok else 'FAIL'} status={f_status}")

    b_ok, b_body, b_critical = check_backend_health()
    lines.append(f"quickcheck.backend_health={'PASS' if b_ok else 'FAIL'} body={b_body}")
    if b_critical:
        critical_fail = True

    m_ok, m_status = check_http_head("https://meeting.aximo.works", "302")
    lines.append(f"quickcheck.cloudflare_meeting={'PASS' if m_ok else 'FAIL'} status={m_status}")

    a_ok, a_status = check_http_head("https://api.aximo.works/tasks", "302")
    lines.append(f"quickcheck.cloudflare_api_tasks={'PASS' if a_ok else 'FAIL'} status={a_status}")

    labels = [
        "com.aximo.frontend",
        "com.aximo.backend",
        "com.aximo.cloudflared",
        "com.aximo.backup_sqlite",
        "com.aximo.daily_brief",
    ]
    lines.append("quickcheck.launchd:")
    lines.extend([f"  - {x}" for x in launchd_summary(labels)])

    # 2) Backup
    backup = run_cmd(["/bin/bash", str(ROOT / "ops" / "backup_sqlite.sh")], timeout=120)
    backup_ok = backup.returncode == 0
    lines.append(f"backup={'SUCCESS' if backup_ok else 'FAIL'} rc={backup.returncode}")

    # 3) Daily brief
    brief = run_cmd([sys.executable, str(ROOT / "ops" / "daily_brief.py")], timeout=180)
    first = ((brief.stdout or "").strip().splitlines() or ["(no output)"])[0]
    brief_state = "OK" if first.startswith("DAILY_BRIEF_OK") else "SKIP" if first.startswith("DAILY_BRIEF_SKIP") else "FAIL"
    lines.append(f"daily_brief={brief_state} rc={brief.returncode} head={first}")

    # 4) Linear post summary
    git_head = run_cmd(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"]).stdout.strip()
    lines.append(f"git_head={git_head}")

    summary_text = "Daily Close Summary\n" + "\n".join(lines)
    linear = run_cmd(
        [
            sys.executable,
            str(ROOT / "scripts" / "post_daily_brief_to_linear.py"),
            "--issue",
            "HKA-38",
            "--text",
            summary_text,
        ],
        timeout=180,
    )
    linear_ok = linear.returncode == 0
    lines.append(f"linear_post={'SUCCESS' if linear_ok else 'FAIL'} rc={linear.returncode}")

    # 5) Optional email
    email_script = ROOT / "scripts" / "send_daily_report_email.py"
    if email_script.exists():
        report = ROOT / "docs" / "reports" / f"AXIMO_DAILY_{datetime.now().strftime('%Y-%m-%d')}.md"
        email = run_cmd([sys.executable, str(email_script), "--report", str(report)], timeout=180)
        email_ok = email.returncode == 0
        lines.append(f"email={'SUCCESS' if email_ok else 'FAIL'} rc={email.returncode}")
    else:
        lines.append("email=SKIP script_missing")

    if critical_fail:
        lines.append("critical=CRITICAL_FAIL backend /health")

    for line in lines:
        log_line(line)

    print("DAILY_CLOSE_DONE")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
