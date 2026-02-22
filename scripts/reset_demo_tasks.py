#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sqlite3
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000"
DB_PATH = Path("/Users/albertkim/02_PROJECTS/03_aximo/backend/aximo.db")


def read_token() -> str:
    env_path = Path("/Users/albertkim/02_PROJECTS/03_aximo/backend/.env")
    if not env_path.exists():
        raise SystemExit("backend/.env not found")
    text = env_path.read_text(encoding="utf-8", errors="ignore")
    m = re.search(r"^AXIMO_API_TOKEN\s*=\s*(.+)\s*$", text, re.M)
    if not m:
        raise SystemExit("AXIMO_API_TOKEN missing")
    token = m.group(1).strip().strip('"').strip("'")
    if not token:
        raise SystemExit("AXIMO_API_TOKEN empty")
    return token


def api_post(path: str, payload: dict, token: str) -> tuple[int, dict]:
    req = urllib.request.Request(
        f"{BASE_URL}{path}",
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={
            "Content-Type": "application/json",
            "X-AXIMO-TOKEN": token,
        },
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        body = json.loads(resp.read().decode("utf-8", errors="replace"))
        return int(resp.getcode() or 0), body


def delete_existing_demo_tasks() -> None:
    if not DB_PATH.exists():
        return
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute("SELECT id, text FROM tasks WHERE text LIKE '[DEMO]%'").fetchall()
        for row in rows:
            task_id = row["id"]
            title = row["text"]
            conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            conn.execute("DELETE FROM tasks WHERE parent_id = ?", (task_id,))
            print(f"status=200 id={task_id} title={title}")
        conn.commit()
    finally:
        conn.close()


def iso_utc(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat()


def create_seed(
    title: str,
    due_date_iso: str,
    done: bool,
    owner: str | None,
    priority: str,
    weight: float,
    token: str,
) -> None:
    status_code, body = api_post(
        "/tasks",
        {
            "text": title,
            "type": "internal_generate",
            "due_date": due_date_iso,
            "owner": owner,
            "priority": priority,
            "weight": weight,
        },
        token,
    )
    task_id = str(body.get("id", ""))
    print(f"status={status_code} id={task_id} title={title}")

    if done and task_id:
        status_code2, body2 = api_post(
            f"/tasks/{task_id}/status",
            {"status": "done"},
            token,
        )
        updated_id = str(body2.get("id", task_id))
        print(f"status={status_code2} id={updated_id} title={title}")


def main() -> None:
    token = read_token()
    now = datetime.now(timezone.utc)

    delete_existing_demo_tasks()

    create_seed(
        "[DEMO] Due Soon HIGH w3 (1h)",
        iso_utc(now + timedelta(hours=1)),
        False,
        "alice",
        "high",
        3.0,
        token,
    )
    create_seed(
        "[DEMO] Due Soon MED w1 (1h)",
        iso_utc(now + timedelta(hours=1)),
        False,
        "bob",
        "medium",
        1.0,
        token,
    )
    create_seed(
        "[DEMO] Due Soon LOW w0.5 (1h)",
        iso_utc(now + timedelta(hours=1)),
        False,
        "carol",
        "low",
        0.5,
        token,
    )
    create_seed(
        "[DEMO] Overdue HIGH w2 (2d ago)",
        iso_utc(now - timedelta(days=2)),
        False,
        "alice",
        "high",
        2.0,
        token,
    )
    create_seed(
        "[DEMO] Done old MED w1 (14d ago)",
        iso_utc(now - timedelta(days=14)),
        True,
        "bob",
        "medium",
        1.0,
        token,
    )


if __name__ == "__main__":
    main()
