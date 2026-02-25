#!/usr/bin/env python3
import os
import json
import sqlite3
from datetime import datetime, timezone
from typing import Optional, Tuple

import urllib.request


DB_PATH = "/Users/albertkim/02_PROJECTS/03_aximo/backend/aximo.db"


def parse_due_date(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    value = value.strip()
    # Accept YYYY-MM-DD as end-of-day local-ish (match frontend behavior roughly)
    if len(value) == 10 and value[4] == "-" and value[7] == "-":
        try:
            y, m, d = map(int, value.split("-"))
            return datetime(y, m, d, 23, 59, 59, 999000, tzinfo=timezone.utc)
        except Exception:
            return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return None


def clamp_weight(w: Optional[float]) -> float:
    try:
        v = float(w if w is not None else 1.0)
    except Exception:
        v = 1.0
    if v < 0.1:
        return 0.1
    if v > 10.0:
        return 10.0
    return v


def normalize_priority(p: Optional[str]) -> str:
    if p in ("low", "medium", "high"):
        return p
    return "medium"


def compute_time_score(due: Optional[datetime], now: datetime) -> int:
    if due is None:
        return 0
    now_ms = int(now.timestamp() * 1000)
    due_ms = int(due.timestamp() * 1000)

    h = 60 * 60 * 1000
    h24 = 24 * h
    h72 = 72 * h

    if due_ms < now_ms:
        return min(999, 100 + ((now_ms - due_ms + h - 1) // h))
    if now_ms <= due_ms < now_ms + h24:
        return min(999, 50 + ((h24 - (due_ms - now_ms) + h - 1) // h))
    if now_ms + h24 <= due_ms < now_ms + h72:
        return min(999, 10 + ((h72 - (due_ms - now_ms) + h - 1) // h))
    return 0


def compute_p2(priority: str, weight: float, time_score: int) -> int:
    priority_factor = 2.0 if priority == "high" else 0.5 if priority == "low" else 1.0
    base = clamp_weight(weight) * priority_factor
    p2 = int((base * time_score + 0.999999))  # ceil-ish
    if p2 < 0:
        return 0
    if p2 > 999:
        return 999
    return p2


def send_telegram(text: str) -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat_id:
        raise RuntimeError("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID")

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        if resp.getcode() != 200:
            body = resp.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Telegram send failed: status={resp.getcode()} body={body[:200]}")


def main() -> int:
    now = datetime.now(timezone.utc)

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT id, text, status, due_date, priority, weight
            FROM tasks
            WHERE status = 'pending_approval'
            ORDER BY created_at DESC
            """
        ).fetchall()

    scored = []
    for r in rows:
        due = parse_due_date(r["due_date"])
        time_score = compute_time_score(due, now)
        prio = normalize_priority(r["priority"])
        w = float(r["weight"]) if r["weight"] is not None else 1.0
        p2 = compute_p2(prio, w, time_score)
        if p2 <= 0:
            continue
        scored.append((p2, r["id"], r["text"]))

    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:3]

    # Compose message
    stamp = datetime.now().strftime("%H:%M")
    if not top:
        msg = f"Execution Pressure Alert ({stamp})\n\nNo pending approvals with pressure."
    else:
        lines = [f"🔥 Execution Pressure Alert ({stamp})", ""]
        for i, (p2, tid, text) in enumerate(top, start=1):
            short = tid[:8]
            title = (text or "").strip().replace("\n", " ")
            if len(title) > 80:
                title = title[:77] + "..."
            lines.append(f"{i}) P:{p2}  {title}  (id:{short})")
        lines.append("")
        lines.append("Approve or reject to reduce pressure.")
        msg = "\n".join(lines)

    send_telegram(msg)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
