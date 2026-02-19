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

  const onCreateTask = async () => {
    setLoading(true);
    setError("");
    setTask(null);

    try {
      const res = await apiFetch("/tasks", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, type: "internal_generate" }),
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
    if (!task || task.status !== "pending_approval") return;

    setApproving(true);
    setError("");

    try {
      const res = await apiFetch(`/tasks/${task.id}/approve`, { method: "POST" });

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
    if (!task || task.status !== "approved") return;

    setRunning(true);
    setError("");

    try {
      const res = await apiFetch(`/tasks/${task.id}/run`, { method: "POST" });

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

  const primaryBtn: React.CSSProperties = {
    padding: "10px 14px",
    borderRadius: 8,
    border: "1px solid #111",
    background: "#111",
    color: "#fff",
    fontWeight: 600,
    cursor: "pointer",
  };

  const secondaryBtn: React.CSSProperties = {
    padding: "10px 14px",
    borderRadius: 8,
    border: "1px solid #111",
    background: "#fff",
    color: "#111",
    fontWeight: 600,
    cursor: "pointer",
  };

  const disabledBtn: React.CSSProperties = {
    opacity: 0.5,
    cursor: "not-allowed",
  };

  return (
    <main style={{ maxWidth: 900, margin: "40px auto", padding: "0 16px" }}>
      <h1 style={{ marginBottom: 12 }}>AXIMO – Admin Employee (MVP-0)</h1>

      <textarea
        placeholder="Enter the founder's instruction..."
        rows={10}
        value={text}
        onChange={(e) => setText(e.target.value)}
        style={{
          width: "100%",
          marginTop: 12,
          padding: 12,
          borderRadius: 10,
          border: "1px solid #ccc",
          fontSize: 16,
        }}
      />

      <div style={{ marginTop: 14 }}>
        <div style={{ fontWeight: 700, marginBottom: 8 }}>Create Task</div>
        <button
          type="button"
          onClick={onCreateTask}
          disabled={loading || running || !text.trim()}
          style={{
            ...primaryBtn,
            ...(loading || running || !text.trim() ? disabledBtn : {}),
          }}
        >
          {loading ? "Creating..." : "Create Task"}
        </button>
      </div>

      <div
        id="result-box"
        style={{
          minHeight: 120,
          marginTop: 16,
          border: "1px solid #ccc",
          padding: 12,
          borderRadius: 10,
          background: "#fafafa",
        }}
      >
        {running ? "Running..." : null}
        {!running && error ? <div style={{ color: "#b00020" }}>{error}</div> : null}
        {!running && !error && task ? (
          <div>
            <div style={{ fontWeight: 700 }}>{`Task ID: ${task.id}`}</div>
            <div style={{ marginTop: 6 }}>{`Status: ${task.status}`}</div>
          </div>
        ) : null}
      </div>

      <div style={{ marginTop: 14 }}>
        <div style={{ fontWeight: 700, marginBottom: 8 }}>Approve / Run (After Approval)</div>

        <button
          type="button"
          onClick={onApprove}
          disabled={!task || task.status !== "pending_approval" || approving || loading || running}
          style={{
            ...secondaryBtn,
            ...((!task || task.status !== "pending_approval" || approving || loading || running) ? disabledBtn : {}),
          }}
        >
          {approving ? "Approving..." : "Approve"}
        </button>

        <button
          type="button"
          onClick={onRunApproved}
          disabled={!task || task.status !== "approved" || running || loading || approving}
          style={{
            ...primaryBtn,
            marginLeft: 10,
            ...((!task || task.status !== "approved" || running || loading || approving) ? disabledBtn : {}),
          }}
        >
          {running ? "Running..." : "Run (After Approval)"}
        </button>
      </div>
    </main>
  );
}
