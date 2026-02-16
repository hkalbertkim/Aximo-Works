from datetime import datetime, timezone
import json
import os
import sqlite3
from typing import Literal
import urllib.error
import urllib.request
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


class IntentRequest(BaseModel):
    text: str


class TaskCreateRequest(BaseModel):
    text: str
    type: Literal["internal_generate", "external_execute"] | None = None


class TaskStatusUpdateRequest(BaseModel):
    status: Literal["pending_approval", "approved", "done"]


class Task(BaseModel):
    id: str
    text: str
    type: Literal["internal_generate", "external_execute"]
    status: Literal["pending_approval", "approved", "done"]
    parent_id: str | None = None
    created_at: str
    output: dict | None = None
    ran_at: str | None = None


class SummaryResult(BaseModel):
    summary: str
    action_items: list[str]
    questions: list[str]


app = FastAPI()

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


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def task_to_db_values(task: Task) -> tuple[str, str, str, str, str | None, str, str | None, str | None]:
    return (
        task.id,
        task.text,
        task.type,
        task.status,
        task.parent_id,
        task.created_at,
        json.dumps(task.output) if task.output is not None else None,
        task.ran_at,
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
                ran_at TEXT NULL
            )
            """
        )
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
    return {"ok": True}


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
    )
    with get_db_connection() as conn:
        conn.execute(
            """
            INSERT INTO tasks (id, text, type, status, parent_id, created_at, output, ran_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            task_to_db_values(task),
        )
        conn.commit()
    return task


@app.get("/tasks")
def list_tasks() -> list[Task]:
    with get_db_connection() as conn:
        rows = conn.execute("SELECT * FROM tasks ORDER BY created_at DESC").fetchall()
    return [row_to_task(row) for row in rows]


@app.post("/tasks/{task_id}/approve")
def approve_task(task_id: str) -> Task:
    with get_db_connection() as conn:
        cur = conn.execute("UPDATE tasks SET status = ? WHERE id = ?", ("approved", task_id))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Task not found")
        conn.commit()
        task = get_task_by_id(conn, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.post("/tasks/{task_id}/status")
def update_task_status(task_id: str, payload: TaskStatusUpdateRequest) -> Task:
    with get_db_connection() as conn:
        task = get_task_by_id(conn, task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")

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

    send_telegram(
        f"Task status updated: {task.text}\n"
        f"Status: {payload.status}\n"
        "Board: https://meeting.aximo.works/kanban"
    )
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
                    INSERT INTO tasks (id, text, type, status, parent_id, created_at, output, ran_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    task_to_db_values(child),
                )

        conn.commit()
        updated = get_task_by_id(conn, task_id)

    if updated is None:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.type == "internal_generate":
        send_telegram(
            "Meeting execution plan generated.\n"
            f"Summary: {result.get('summary', '')}\n"
            "Tasks created: 3\n"
            "Board: https://meeting.aximo.works/kanban"
        )

    return updated
