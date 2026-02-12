from datetime import datetime, timezone
import json
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


class Task(BaseModel):
    id: str
    text: str
    status: Literal["pending_approval", "approved", "done"]
    created_at: str
    output: dict | None = None
    ran_at: str | None = None


class SummaryResult(BaseModel):
    summary: str
    action_items: list[str]
    questions: list[str]


app = FastAPI()
tasks: list[Task] = []


def build_summary_prompt(text: str, action_items_count: int, questions_count: int) -> str:
    return (
        "You must output ONLY valid JSON. No prose, no markdown, no code fences.\n"
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
                    "Output exactly one JSON object with keys:\n"
                    "- summary: string\n"
                    "- action_items: array of exactly 3 strings\n"
                    "- questions: array of exactly 2 strings\n\n"
                    f"Original task:\n{prompt}"
                )
                continue
            return fallback
    return fallback

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
        status="pending_approval",
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    tasks.append(task)
    return task


@app.get("/tasks")
def list_tasks() -> list[Task]:
    return list(reversed(tasks))


@app.post("/tasks/{task_id}/approve")
def approve_task(task_id: str) -> Task:
    for i, task in enumerate(tasks):
        if task.id == task_id:
            updated = task.model_copy(update={"status": "approved"})
            tasks[i] = updated
            return updated
    raise HTTPException(status_code=404, detail="Task not found")


@app.post("/tasks/{task_id}/run")
def run_task(task_id: str) -> Task:
    for i, task in enumerate(tasks):
        if task.id == task_id:
            if task.status != "approved":
                raise HTTPException(status_code=409, detail="Task must be approved before run")
            result = call_ollama_structured(
                build_summary_prompt(task.text, action_items_count=3, questions_count=2)
            )
            updated = task.model_copy(
                update={
                    "status": "done",
                    "output": result,
                    "ran_at": datetime.now(timezone.utc).isoformat(),
                }
            )
            tasks[i] = updated
            return updated
    raise HTTPException(status_code=404, detail="Task not found")
