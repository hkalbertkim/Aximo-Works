from datetime import datetime, timezone
import json
import os
import sqlite3
from typing import Literal
import urllib.error
import urllib.request
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.middleware.base import BaseHTTPMiddleware
from telegram_notify import send_telegram as send_telegram_notify


class IntentRequest(BaseModel):
    text: str


class TaskCreateRequest(BaseModel):
    text: str
    type: Literal["internal_generate", "external_execute"] | None = None
    due_date: str | None = None
    owner: str | None = None
    priority: Literal["low", "medium", "high"] | None = None
    weight: float | None = None


class TaskStatusUpdateRequest(BaseModel):
    status: Literal["pending_approval", "approved", "done"]


class TaskRejectRequest(BaseModel):
    reason: str | None = None


class Task(BaseModel):
    id: str
    text: str
    type: Literal["internal_generate", "external_execute"]
    status: Literal["pending_approval", "approved", "done"]
    parent_id: str | None = None
    created_at: str
    output: dict | None = None
    ran_at: str | None = None
    due_date: str | None = None
    owner: str | None = None
    priority: Literal["low", "medium", "high"] = "medium"
    weight: float = 1.0
    approved_at: str | None = None
    approved_by: str | None = None
    rejected_at: str | None = None
    rejected_by: str | None = None
    reject_reason: str | None = None


class SummaryResult(BaseModel):
    summary: str
    action_items: list[str]
    questions: list[str]


app = FastAPI()
AXIMO_API_TOKEN = os.getenv("AXIMO_API_TOKEN", "").strip()
AXIMO_IP_ALLOWLIST = [ip.strip() for ip in os.getenv("AXIMO_IP_ALLOWLIST", "").split(",") if ip.strip()]


class AximoAPIGuard(BaseHTTPMiddleware):
    PUBLIC_PATHS = {"/health", "/telegram/health", "/telegram/webhook", "/docs", "/redoc", "/openapi.json"}

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if path in self.PUBLIC_PATHS or path.startswith("/docs") or path.startswith("/redoc"):
            return await call_next(request)

        if AXIMO_IP_ALLOWLIST:
            # Prefer reverse-proxy headers
            xff = request.headers.get("x-forwarded-for")
            if xff:
                client_ip = xff.split(",")[0].strip()
            else:
                xri = request.headers.get("x-real-ip")
                client_ip = (xri or "").strip() if xri else (request.client.host if request.client else "")

            loopback_ips = {"127.0.0.1", "::1", "::ffff:127.0.0.1"}
            if client_ip not in loopback_ips and client_ip not in AXIMO_IP_ALLOWLIST:
                return JSONResponse(status_code=403, content={"detail": "IP not allowed"})

        if not AXIMO_API_TOKEN:
            return JSONResponse(status_code=500, content={"detail": "AXIMO_API_TOKEN is not configured"})

        incoming = request.headers.get("x-aximo-token", "")
        if incoming != AXIMO_API_TOKEN:
            return JSONResponse(status_code=401, content={"detail": "Unauthorized"})

        return await call_next(request)


app.add_middleware(AximoAPIGuard)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://meeting.aximo.works",
        "http://meeting.aximo.works",
        "https://api.aximo.works",
        "http://api.aximo.works",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "/Users/albertkim/02_PROJECTS/03_aximo/backend/aximo.db"
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TELEGRAM_WEBHOOK_SECRET = os.getenv("TELEGRAM_WEBHOOK_SECRET", "").strip()


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def normalize_priority(priority: str | None) -> Literal["low", "medium", "high"]:
    if priority in ("low", "medium", "high"):
        return priority
    return "medium"


def clamp_weight(weight: float | None) -> float:
    if weight is None:
        return 1.0
    try:
        value = float(weight)
    except Exception:
        return 1.0
    if value < 0.1:
        return 0.1
    if value > 10.0:
        return 10.0
    return value


def task_to_db_values(
    task: Task,
) -> tuple[str, str, str, str, str | None, str, str | None, str | None, str | None, str | None, str, float, str | None, str | None, str | None, str | None, str | None]:
    return (
        task.id,
        task.text,
        task.type,
        task.status,
        task.parent_id,
        task.created_at,
        json.dumps(task.output) if task.output is not None else None,
        task.ran_at,
        task.due_date,
        task.owner,
        normalize_priority(task.priority),
        clamp_weight(task.weight),
        task.approved_at,
        task.approved_by,
        task.rejected_at,
        task.rejected_by,
        task.reject_reason,
    )


def row_to_task(row: sqlite3.Row) -> Task:
    output = None
    if row["output"] is not None:
        output = json.loads(row["output"])
    return Task(
        id=row["id"],
        text=row["text"],
        type=row["type"],
        status=row["status"],
        parent_id=row["parent_id"],
        created_at=row["created_at"],
        output=output,
        ran_at=row["ran_at"],
        due_date=row["due_date"],
        owner=row["owner"] if "owner" in row.keys() else None,
        priority=normalize_priority(row["priority"] if "priority" in row.keys() else None),
        weight=clamp_weight(row["weight"] if "weight" in row.keys() else None),
        approved_at=row["approved_at"] if "approved_at" in row.keys() else None,
        approved_by=row["approved_by"] if "approved_by" in row.keys() else None,
        rejected_at=row["rejected_at"] if "rejected_at" in row.keys() else None,
        rejected_by=row["rejected_by"] if "rejected_by" in row.keys() else None,
        reject_reason=row["reject_reason"] if "reject_reason" in row.keys() else None,
    )


def get_task_by_id(conn: sqlite3.Connection, task_id: str) -> Task | None:
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if row is None:
        return None
    return row_to_task(row)


@app.on_event("startup")
def init_db() -> None:
    with get_db_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                text TEXT NOT NULL,
                type TEXT NOT NULL,
                status TEXT NOT NULL,
                parent_id TEXT NULL,
                created_at TEXT NOT NULL,
                output TEXT NULL,
                ran_at TEXT NULL,
                due_date TEXT NULL,
                owner TEXT NULL,
                priority TEXT NOT NULL DEFAULT 'medium',
                weight REAL NOT NULL DEFAULT 1.0,
                approved_at TEXT NULL,
                approved_by TEXT NULL,
                rejected_at TEXT NULL,
                rejected_by TEXT NULL,
                reject_reason TEXT NULL
            )
            """
        )
        columns = {row["name"] for row in conn.execute("PRAGMA table_info(tasks)").fetchall()}
        if "due_date" not in columns:
            conn.execute("ALTER TABLE tasks ADD COLUMN due_date TEXT NULL")
        if "owner" not in columns:
            conn.execute("ALTER TABLE tasks ADD COLUMN owner TEXT NULL")
        if "priority" not in columns:
            conn.execute("ALTER TABLE tasks ADD COLUMN priority TEXT NOT NULL DEFAULT 'medium'")
        if "weight" not in columns:
            conn.execute("ALTER TABLE tasks ADD COLUMN weight REAL NOT NULL DEFAULT 1.0")
        if "approved_at" not in columns:
            conn.execute("ALTER TABLE tasks ADD COLUMN approved_at TEXT NULL")
        if "approved_by" not in columns:
            conn.execute("ALTER TABLE tasks ADD COLUMN approved_by TEXT NULL")
        if "rejected_at" not in columns:
            conn.execute("ALTER TABLE tasks ADD COLUMN rejected_at TEXT NULL")
        if "rejected_by" not in columns:
            conn.execute("ALTER TABLE tasks ADD COLUMN rejected_by TEXT NULL")
        if "reject_reason" not in columns:
            conn.execute("ALTER TABLE tasks ADD COLUMN reject_reason TEXT NULL")
        conn.execute("UPDATE tasks SET priority = 'medium' WHERE priority IS NULL OR priority NOT IN ('low','medium','high')")
        conn.execute("UPDATE tasks SET weight = 1.0 WHERE weight IS NULL")
        conn.execute("UPDATE tasks SET weight = 0.1 WHERE weight < 0.1")
        conn.execute("UPDATE tasks SET weight = 10.0 WHERE weight > 10.0")
        conn.commit()


def send_telegram(text: str) -> None:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("TELEGRAM disabled: missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            status = resp.getcode()
            body = resp.read().decode("utf-8", errors="replace")
            if status != 200:
                print(f"TELEGRAM send failed: status={status} body={body}")
    except Exception as e:
        print(f"TELEGRAM exception: {repr(e)}")
        return


def notify_telegram(text: str) -> None:
    send_telegram(text)


def telegram_api_post(method: str, payload: dict) -> tuple[int | None, str]:
    if not TELEGRAM_BOT_TOKEN:
        return None, "missing TELEGRAM_BOT_TOKEN"
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/{method}"
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            status = resp.getcode()
            body = resp.read().decode("utf-8", errors="replace")
            return status, body
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        return int(e.code), body
    except Exception as e:
        return None, repr(e)


def send_telegram_to_chat(chat_id: str | int, text: str, reply_markup: dict | None = None) -> None:
    payload: dict = {"chat_id": str(chat_id), "text": text}
    if reply_markup is not None:
        payload["reply_markup"] = reply_markup
    status, body = telegram_api_post("sendMessage", payload)
    if status != 200:
        print(f"TELEGRAM send failed: status={status} body={body[:200]}")


def send_task_created_telegram(task: Task) -> None:
    if not TELEGRAM_CHAT_ID:
        return
    text = (
        f"Task Created: {task_title(task)} (id:{short_id(task.id)})\n"
        f"Due: {task.due_date or '-'}"
    )
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "✅ Approve", "callback_data": f"APPROVE:{task.id}"},
                {"text": "❌ Reject", "callback_data": f"REJECT:{task.id}"},
            ]
        ]
    }
    send_telegram_to_chat(TELEGRAM_CHAT_ID, text, reply_markup=keyboard)


def short_id(task_id: str) -> str:
    return task_id[:8]


def task_title(task: Task) -> str:
    return getattr(task, "title", task.text)


def build_summary_prompt(text: str, action_items_count: int, questions_count: int) -> str:
    return (
        "You must output ONLY valid JSON. No prose, no markdown, no code fences.\n"
        "Output language must be English only.\n"
        "If user input is not English, first translate the content into English before summarizing.\n"
        "Output exactly one JSON object with keys:\n"
        "- summary: string\n"
        f"- action_items: array of exactly {action_items_count} strings\n"
        f"- questions: array of exactly {questions_count} strings\n\n"
        f"User input:\n{text}"
    )


def validate_and_normalize_result(raw: dict) -> dict:
    parsed = SummaryResult.model_validate(raw)
    if len(parsed.action_items) != 3:
        raise ValueError("action_items must have exactly 3 items")
    if len(parsed.questions) != 2:
        raise ValueError("questions must have exactly 2 items")
    return parsed.model_dump()


def approve_task_internal(task_id: str, approved_by: str = "admin") -> Task:
    with get_db_connection() as conn:
        task = get_task_by_id(conn, task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        if task.status == "done":
            raise HTTPException(status_code=409, detail="Task already done")
        if task.status == "approved":
            return task
        approved_at = datetime.now(timezone.utc).isoformat()
        conn.execute(
            """
            UPDATE tasks
            SET status = ?, approved_at = ?, approved_by = ?,
                rejected_at = NULL, rejected_by = NULL, reject_reason = NULL
            WHERE id = ?
            """,
            ("approved", approved_at, approved_by, task_id),
        )
        conn.commit()
        updated = get_task_by_id(conn, task_id)
    if updated is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated


def reject_task_internal(task_id: str, reason: str | None, rejected_by: str = "admin") -> Task:
    with get_db_connection() as conn:
        task = get_task_by_id(conn, task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        if task.status == "done":
            raise HTTPException(status_code=409, detail="Task already done")
        rejected_at = datetime.now(timezone.utc).isoformat()
        reject_reason = (reason or "")[:500] or None
        conn.execute(
            """
            UPDATE tasks
            SET status = ?, rejected_at = ?, rejected_by = ?, reject_reason = ?
            WHERE id = ?
            """,
            ("pending_approval", rejected_at, rejected_by, reject_reason, task_id),
        )
        conn.commit()
        updated = get_task_by_id(conn, task_id)
    if updated is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated


def _ollama_generate_response(prompt: str) -> str:
    body = {
        "model": "qwen2.5:7b-instruct",
        "prompt": prompt,
        "stream": False,
    }
    req = urllib.request.Request(
        "http://localhost:11434/api/generate",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=60) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    raw = payload.get("response")
    if not isinstance(raw, str):
        raise ValueError("missing response")
    return raw


def call_ollama_structured(prompt: str) -> dict:
    fallback = {
        "summary": "(Fallback) Unable to generate structured output reliably.",
        "action_items": [
            "(Fallback) Review meeting notes",
            "(Fallback) Assign owners",
            "(Fallback) Confirm deadlines",
        ],
        "questions": [
            "(Fallback) What is the top priority?",
            "(Fallback) What is the deadline?",
        ],
    }

    current_prompt = prompt
    for attempt in range(2):
        try:
            raw_response = _ollama_generate_response(current_prompt)
            raw_json = json.loads(raw_response)
            if not isinstance(raw_json, dict):
                raise ValueError("response is not object")
            return validate_and_normalize_result(raw_json)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, ValueError):
            if attempt == 0:
                current_prompt = (
                    "REPAIR: Previous output was invalid.\n"
                    "Output ONLY valid JSON. No prose, no markdown, no code fences.\n"
                    "Output language must be English only.\n"
                    "If user input is not English, first translate the content into English before summarizing.\n"
                    "Output exactly one JSON object with keys:\n"
                    "- summary: string\n"
                    "- action_items: array of exactly 3 strings\n"
                    "- questions: array of exactly 2 strings\n\n"
                    f"Original task:\n{prompt}"
                )
                continue
            return fallback
    return fallback


@app.get("/health")
def health() -> dict:
    return {
        "ok": True,
        "ts": datetime.now(timezone.utc).isoformat(),
        "service": "aximo-backend",
    }


@app.get("/telegram/health")
def telegram_health() -> dict:
    if not TELEGRAM_BOT_TOKEN:
        return {"ok": False, "error_code": 0, "body": "missing TELEGRAM_BOT_TOKEN"}

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe"
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw_body = resp.read().decode("utf-8", errors="replace")
            payload = json.loads(raw_body)
            username = payload.get("result", {}).get("username", "")
            if resp.getcode() == 200 and payload.get("ok") is True:
                return {"ok": True, "username": username}
            return {"ok": False, "error_code": int(resp.getcode() or 0), "body": raw_body[:200]}
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        return {"ok": False, "error_code": int(e.code), "body": body[:200]}
    except Exception as e:
        return {"ok": False, "error_code": 0, "body": repr(e)[:200]}


@app.post("/intent")
def intent(payload: IntentRequest) -> dict:
    result = call_ollama_structured(build_summary_prompt(payload.text, action_items_count=3, questions_count=2))
    return {
        "employee": "Admin Employee",
        "intent": "summarize",
        "input": payload.text,
        "result": result,
    }


@app.post("/tasks")
def create_task(payload: TaskCreateRequest) -> Task:
    task = Task(
        id=str(uuid4()),
        text=payload.text,
        type=payload.type or "internal_generate",
        status="pending_approval",
        created_at=datetime.now(timezone.utc).isoformat(),
        due_date=payload.due_date,
        owner=payload.owner,
        priority=normalize_priority(payload.priority),
        weight=clamp_weight(payload.weight),
    )
    with get_db_connection() as conn:
        conn.execute(
            """
            INSERT INTO tasks (
                id, text, type, status, parent_id, created_at, output, ran_at,
                due_date, owner, priority, weight, approved_at, approved_by,
                rejected_at, rejected_by, reject_reason
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            task_to_db_values(task),
        )
        conn.commit()
    send_task_created_telegram(task)
    task_title = getattr(task, "title", task.text)
    send_telegram_notify(
        f"🆕 Task Created\nTitle: {task_title}\nStatus: {task.status}\nBoard: https://meeting.aximo.works/kanban"
    )
    return task


@app.get("/tasks")
def list_tasks() -> list[Task]:
    with get_db_connection() as conn:
        rows = conn.execute("SELECT * FROM tasks ORDER BY created_at DESC").fetchall()
    return [row_to_task(row) for row in rows]


@app.post("/tasks/{task_id}/approve")
def approve_task(task_id: str) -> Task:
    task = approve_task_internal(task_id, approved_by="admin")
    send_telegram_notify(f"✅ Approved: {task_title(task)} (id:{short_id(task.id)})")
    return task


@app.post("/tasks/{task_id}/reject")
def reject_task(task_id: str, payload: TaskRejectRequest) -> Task:
    updated = reject_task_internal(task_id, payload.reason, rejected_by="admin")
    return updated


@app.post("/telegram/webhook")
async def telegram_webhook(request: Request) -> JSONResponse:
    secret = request.headers.get("X-Telegram-Secret", "").strip()
    if not TELEGRAM_WEBHOOK_SECRET or secret != TELEGRAM_WEBHOOK_SECRET:
        return JSONResponse(status_code=401, content={"detail": "Unauthorized"})

    try:
        update = await request.json()
    except Exception:
        return JSONResponse(status_code=200, content={"ok": True})

    try:
        callback_query = update.get("callback_query") if isinstance(update, dict) else None
        if isinstance(callback_query, dict):
            data = str(callback_query.get("data") or "")
            message = callback_query.get("message") or {}
            chat = message.get("chat") or {}
            chat_id = chat.get("id")

            if data.startswith("APPROVE:"):
                task_id = data.split(":", 1)[1].strip()
                try:
                    updated = approve_task_internal(task_id, approved_by="admin")
                    if chat_id is not None:
                        send_telegram_to_chat(chat_id, f"✅ Approved: {task_title(updated)} (id:{short_id(updated.id)})")
                except HTTPException as e:
                    if chat_id is not None:
                        send_telegram_to_chat(chat_id, f"Approve failed (id:{short_id(task_id)}): {e.detail}")
            elif data.startswith("REJECT:"):
                task_id = data.split(":", 1)[1].strip()
                if chat_id is not None:
                    send_telegram_to_chat(chat_id, f"Reply with: REJECT_REASON:{task_id}:<your reason>")

            return JSONResponse(status_code=200, content={"ok": True})

        message = update.get("message") if isinstance(update, dict) else None
        if isinstance(message, dict):
            text = str(message.get("text") or "")
            chat = message.get("chat") or {}
            chat_id = chat.get("id")
            if text.startswith("REJECT_REASON:"):
                parts = text.split(":", 2)
                if len(parts) >= 3:
                    task_id = parts[1].strip()
                    reason = parts[2].strip()
                    try:
                        updated = reject_task_internal(task_id, reason, rejected_by="admin")
                        if chat_id is not None:
                            send_telegram_to_chat(chat_id, f"❌ Rejected: {task_title(updated)} (id:{short_id(updated.id)})")
                    except HTTPException as e:
                        if chat_id is not None:
                            send_telegram_to_chat(chat_id, f"Reject failed (id:{short_id(task_id)}): {e.detail}")
                elif chat_id is not None:
                    send_telegram_to_chat(chat_id, "Reply with: REJECT_REASON:<task_id>:<your reason>")
    except Exception:
        pass

    return JSONResponse(status_code=200, content={"ok": True})


@app.post("/tasks/{task_id}/status")
def update_task_status(task_id: str, payload: TaskStatusUpdateRequest) -> Task:
    with get_db_connection() as conn:
        task = get_task_by_id(conn, task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        previous_status = task.status

        conn.execute("UPDATE tasks SET status = ? WHERE id = ?", (payload.status, task_id))
        updated = get_task_by_id(conn, task_id)
        if updated is None:
            raise HTTPException(status_code=404, detail="Task not found")

        if updated.parent_id:
            child_rows = conn.execute(
                "SELECT status FROM tasks WHERE parent_id = ?",
                (updated.parent_id,),
            ).fetchall()
            if child_rows and all(row["status"] == "done" for row in child_rows):
                conn.execute("UPDATE tasks SET status = ? WHERE id = ?", ("done", updated.parent_id))

        conn.commit()

    if previous_status != payload.status:
        send_telegram_notify(f"🔄 Status: {task_title(updated)} → {payload.status} (id:{short_id(updated.id)})")
        if payload.status == "done":
            send_telegram_notify(f"🎉 Done: {task_title(updated)} (id:{short_id(updated.id)})")
    return updated


@app.post("/tasks/{task_id}/run")
def run_task(task_id: str) -> Task:
    with get_db_connection() as conn:
        task = get_task_by_id(conn, task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")

        if task.type == "external_execute" and task.status != "approved":
            raise HTTPException(status_code=409, detail="Task must be approved before run")

        result = call_ollama_structured(
            build_summary_prompt(task.text, action_items_count=3, questions_count=2)
        )
        ran_at = datetime.now(timezone.utc).isoformat()
        next_status: Literal["pending_approval", "approved", "done"] = (
            "approved" if task.type == "internal_generate" else "done"
        )

        conn.execute(
            "UPDATE tasks SET status = ?, output = ?, ran_at = ? WHERE id = ?",
            (next_status, json.dumps(result), ran_at, task_id),
        )

        if task.type == "internal_generate":
            for item in result.get("action_items", []):
                child = Task(
                    id=str(uuid4()),
                    text=str(item),
                    type="internal_generate",
                    status="pending_approval",
                    parent_id=task.id,
                    created_at=ran_at,
                )
                conn.execute(
                    """
                    INSERT INTO tasks (
                        id, text, type, status, parent_id, created_at, output, ran_at,
                        due_date, owner, priority, weight, approved_at, approved_by,
                        rejected_at, rejected_by, reject_reason
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    task_to_db_values(child),
                )

        conn.commit()
        updated = get_task_by_id(conn, task_id)

    if updated is None:
        raise HTTPException(status_code=404, detail="Task not found")

    send_telegram_notify(f"▶️ Running: {task_title(updated)} (id:{short_id(updated.id)})")

    return updated
