"use client";

import { useState } from "react";

type Task = {
  id: string;
  text: string;
  status: "pending_approval" | "approved" | "done";
  created_at: string;
  output?:
    | {
        summary?: string;
        action_items?: string[];
        questions?: string[];
      }
    | null;
  ran_at?: string | null;
};

export default function Home() {
  const [text, setText] = useState("");
  const [task, setTask] = useState<Task | null>(null);
  const [loading, setLoading] = useState(false);
  const [approving, setApproving] = useState(false);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState("");

  const onRun = async () => {
    setLoading(true);
    setError("");
    setTask(null);

    try {
      const res = await fetch("http://localhost:8000/tasks", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }

      const data: Task = await res.json();
      setTask(data);
    } catch (e) {
      const message = e instanceof Error ? e.message : "Unknown error";
      setError(`요청 실패: ${message}`);
    } finally {
      setLoading(false);
    }
  };

  const onApprove = async () => {
    if (!task || task.status !== "pending_approval") {
      return;
    }

    setApproving(true);
    setError("");

    try {
      const res = await fetch(`http://localhost:8000/tasks/${task.id}/approve`, {
        method: "POST",
      });

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }

      const data: Task = await res.json();
      setTask(data);
    } catch (e) {
      const message = e instanceof Error ? e.message : "Unknown error";
      setError(`승인 실패: ${message}`);
    } finally {
      setApproving(false);
    }
  };

  const onRunApproved = async () => {
    if (!task || task.status !== "approved") {
      return;
    }

    setRunning(true);
    setError("");

    try {
      const res = await fetch(`http://localhost:8000/tasks/${task.id}/run`, {
        method: "POST",
      });

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }

      const data: Task = await res.json();
      setTask(data);
    } catch (e) {
      const message = e instanceof Error ? e.message : "Unknown error";
      setError(`실행 실패: ${message}`);
    } finally {
      setRunning(false);
    }
  };

  return (
    <main style={{ maxWidth: "720px", margin: "40px auto", padding: "0 16px" }}>
      <h1>AXIMO – Admin Employee (MVP-0)</h1>
      <textarea
        placeholder="대표님의 지시를 입력하세요..."
        rows={8}
        value={text}
        onChange={(e) => setText(e.target.value)}
        style={{ width: "100%", marginTop: "16px", padding: "12px" }}
      />
      <div style={{ marginTop: "12px" }}>
        <button type="button" onClick={onRun} disabled={loading}>
          실행
        </button>
      </div>
      <div
        id="result-box"
        style={{ minHeight: "120px", marginTop: "16px", border: "1px solid #ccc", padding: "12px" }}
      >
        {loading || running ? "실행 중..." : null}
        {!loading && !running && error ? error : null}
        {!loading && !running && !error && task ? (
          <div>
            <div>{`승인 대기: ${task.id}`}</div>
            <div>{`상태: ${task.status}`}</div>
            {task.output && typeof task.output === "object" ? (
              <div style={{ marginTop: "8px" }}>
                <div>{`Summary: ${task.output.summary ?? ""}`}</div>
                <div style={{ marginTop: "8px" }}>Action Items:</div>
                <ul>
                  {(task.output.action_items ?? []).map((item, idx) => (
                    <li key={`action-${idx}`}>{item}</li>
                  ))}
                </ul>
                <div style={{ marginTop: "8px" }}>Questions:</div>
                <ul>
                  {(task.output.questions ?? []).map((q, idx) => (
                    <li key={`question-${idx}`}>{q}</li>
                  ))}
                </ul>
              </div>
            ) : null}
          </div>
        ) : null}
      </div>
      <div style={{ marginTop: "12px" }}>
        <button
          type="button"
          onClick={onApprove}
          disabled={!task || task.status !== "pending_approval" || approving || loading || running}
        >
          승인
        </button>
        <button
          type="button"
          onClick={onRunApproved}
          disabled={!task || task.status !== "approved" || running || loading || approving}
          style={{ marginLeft: "8px" }}
        >
          실행(승인 후)
        </button>
      </div>
    </main>
  );
}
