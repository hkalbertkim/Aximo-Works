#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

BASE = "http://127.0.0.1:8000"


def read_aximo_token() -> str:
    env_path = Path("backend/.env")
    if not env_path.exists():
        raise SystemExit("backend/.env not found")
    txt = env_path.read_text(encoding="utf-8", errors="ignore")
    m = re.search(r"^AXIMO_API_TOKEN\s*=\s*(.+)\s*$", txt, re.M)
    if not m:
        raise SystemExit("AXIMO_API_TOKEN missing in backend/.env")
    token = m.group(1).strip().strip('"').strip("'")
    if not token:
        raise SystemExit("AXIMO_API_TOKEN is empty")
    return token


def post_json(path: str, payload: dict, token: str) -> tuple[int, dict]:
    req = urllib.request.Request(
        f"{BASE}{path}",
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={
            "Content-Type": "application/json",
            "X-AXIMO-TOKEN": token,
        },
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        status = int(resp.getcode() or 0)
        body = json.loads(resp.read().decode("utf-8", errors="replace"))
    return status, body


def iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat()


def main() -> None:
    token = read_aximo_token()
    now = datetime.now(timezone.utc)

    seed_defs = [
        ("[DEMO] Overdue (2h ago)", iso(now - timedelta(hours=2)), False),
        ("[DEMO] Due Soon (6h)", iso(now + timedelta(hours=6)), False),
        ("[DEMO] Upcoming (48h)", iso(now + timedelta(hours=48)), False),
        ("[DEMO] Done old (10d ago)", iso(now - timedelta(days=10)), True),
    ]

    for title, due_date, mark_done in seed_defs:
        create_status, created = post_json(
            "/tasks",
            {"text": title, "type": "internal_generate", "due_date": due_date},
            token,
        )
        task_id = str(created.get("id", ""))
        print(f"create status={create_status} id={task_id[:8]} title={title}")

        if mark_done and task_id:
            status_code, _ = post_json(
                f"/tasks/{task_id}/status",
                {"status": "done"},
                token,
            )
            print(f"status-update status={status_code} id={task_id[:8]} title={title} -> done")

    print("Open /kanban and verify badges + Done hidden; click Archived to reveal.")


if __name__ == "__main__":
    main()
