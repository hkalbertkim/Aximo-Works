#!/usr/bin/env python3
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "backend"))
from telegram_notify import send_telegram  # noqa: E402

OFFSET_PATH = REPO_ROOT / "backend" / "data" / "telegram_offset.txt"
KANBAN_URL = "https://meeting.aximo.works/kanban"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def log(msg: str) -> None:
    print(f"[{now_iso()}] {msg}")


def require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required env var: {name}")
    return value


def read_offset(path: Path) -> int:
    if not path.exists():
        return 0
    try:
        return int(path.read_text(encoding="utf-8").strip() or "0")
    except Exception:
        return 0


def write_offset(path: Path, value: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(str(value), encoding="utf-8")


def telegram_request(token: str, method: str, params: dict[str, Any]) -> dict[str, Any]:
    url = f"https://api.telegram.org/bot{token}/{method}"
    data = urllib.parse.urlencode(params).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    with urllib.request.urlopen(req, timeout=35) as resp:
        body = resp.read().decode("utf-8", errors="replace")
    return json.loads(body)


def backend_post_json(base: str, token: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    url = f"{base.rstrip('/')}{path}"
    body = b""
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "X-AXIMO-TOKEN": token,
        },
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
    return json.loads(raw)


def message_text(msg: dict[str, Any]) -> str:
    text = msg.get("text") or msg.get("caption") or ""
    text = str(text).replace("\n", " ").strip()
    return text[:180]


def speaker_name(msg: dict[str, Any]) -> str:
    frm = msg.get("from") or {}
    return str(frm.get("username") or frm.get("first_name") or "unknown")


def build_summary_input(buffer: deque[dict[str, str]]) -> str:
    recent = [m for m in list(buffer)[-20:] if m.get("text") and not m["text"].startswith("/")]
    if not recent:
        return "Telegram thread summary requested, but no recent non-command messages were available."
    lines = [f"- {m['speaker']}: {m['text']}" for m in recent]
    return "Summarize this Telegram group thread into an execution plan:\n" + "\n".join(lines)


def handle_aximo_command(
    backend_base: str,
    aximo_api_token: str,
    buffer: deque[dict[str, str]],
) -> None:
    try:
        text = build_summary_input(buffer)
        created = backend_post_json(
            backend_base,
            aximo_api_token,
            "/tasks",
            {"text": text, "type": "internal_generate"},
        )
        task_id = str(created.get("id", ""))
        if task_id:
            backend_post_json(backend_base, aximo_api_token, f"/tasks/{task_id}/run", None)
        send_telegram(f"🧠 Aximo captured this thread → Board: {KANBAN_URL}")
        log("aximo command processed")
    except Exception:
        log("aximo command processing failed")


def run_worker(duration_seconds: int) -> None:
    tg_token = require_env("TELEGRAM_BOT_TOKEN")
    tg_chat_id = require_env("TELEGRAM_CHAT_ID")
    aximo_api_token = require_env("AXIMO_API_TOKEN")
    backend_base = os.getenv("AXIMO_BACKEND_BASE", "http://127.0.0.1:8000").strip() or "http://127.0.0.1:8000"

    buffer: deque[dict[str, str]] = deque(maxlen=50)
    offset = read_offset(OFFSET_PATH)
    deadline = time.time() + duration_seconds

    log(f"worker start duration={duration_seconds}s offset={offset}")
    while time.time() < deadline:
        params: dict[str, Any] = {
            "timeout": 25,
            "limit": 20,
        }
        if offset > 0:
            params["offset"] = offset

        try:
            resp = telegram_request(tg_token, "getUpdates", params)
        except Exception:
            log("getUpdates failed")
            time.sleep(2)
            continue

        if not resp.get("ok"):
            log("getUpdates returned not ok")
            time.sleep(2)
            continue

        updates = resp.get("result", []) or []
        if not updates:
            continue

        for upd in updates:
            update_id = int(upd.get("update_id", 0))
            if update_id:
                offset = max(offset, update_id + 1)
                write_offset(OFFSET_PATH, offset)

            msg = upd.get("message") or upd.get("edited_message") or {}
            chat = msg.get("chat") or {}
            chat_id = str(chat.get("id", ""))
            text = message_text(msg)

            log(f"update_id={update_id} has_message={bool(msg)} target_chat={chat_id == tg_chat_id}")

            if not msg or chat_id != tg_chat_id:
                continue

            if text:
                buffer.append({"speaker": speaker_name(msg), "text": text})
                log(f"buffer_size={len(buffer)}")

            if text.strip().lower() == "/aximo":
                handle_aximo_command(backend_base, aximo_api_token, buffer)

    log("worker stop")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--duration-seconds", type=int, default=120)
    args = parser.parse_args()
    run_worker(args.duration_seconds)


if __name__ == "__main__":
    main()
