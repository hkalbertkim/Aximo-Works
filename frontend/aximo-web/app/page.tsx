"use client";

import { useState } from "react";
import { apiFetch } from "@/lib/api";

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
      const res = await apiFetch("/tasks", {
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
      setError(`Request failed: ${message}`);
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
      const res = await apiFetch(`/tasks/${task.id}/approve`, {
        method: "POST",
      });

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }

      const data: Task = await res.json();
      setTask(data);
    } catch (e) {
      const message = e instanceof Error ? e.message : "Unknown error";
      setError(`Approval failed: ${message}`);
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
      const res = await apiFetch(`/tasks/${task.id}/run`, {
        method: "POST",
      });

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }

      const data: Task = await res.json();
      setTask(data);
    } catch (e) {
      const message = e instanceof Error ? e.message : "Unknown error";
      setError(`Run failed: ${message}`);
    } finally {
      setRunning(false);
    }
  };

  return (
    <main style={{ maxWidth: "720px", margin: "40px auto", padding: "0 16px" }}>
      <h1>AXIMO – Admin Employee (MVP-0)</h1>
      <textarea
        placeholder="Enter the founder's instruction..."
        rows={8}
        value={text}
        onChange={(e) => setText(e.target.value)}
        style={{ width: "100%", marginTop: "16px", padding: "12px" }}
      />
      <div style={{ marginTop: "12px" }}>
        <button type="button" onClick={onRun} disabled={loading}>
          Create Task
        </button>
      </div>
      <div
        id="result-box"
        style={{ minHeight: "120px", marginTop: "16px", border: "1px solid #ccc", padding: "12px" }}
      >
        {loading || running ? "Running..." : null}
        {!loading && !running && error ? error : null}
        {!loading && !running && !error && task ? (
          <div>
            <div>{`Task ID: ${task.id}`}</div>
            <div>{`Status: ${task.status}`}</div>
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
          Approve
        </button>
        <button
          type="button"
          onClick={onRunApproved}
          disabled={!task || task.status !== "approved" || running || loading || approving}
          style={{ marginLeft: "8px" }}
        >
          Run (After Approval)
        </button>
      </div>
    </main>
  );
}
