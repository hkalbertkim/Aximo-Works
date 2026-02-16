"use client";

import { useState } from "react";

type TaskCreateResponse = {
  id: string;
};

const API_BASE = "http://localhost:8000";

export default function MeetingPage() {
  const [notes, setNotes] = useState("");
  const [running, setRunning] = useState(false);
  const [status, setStatus] = useState("");

  const onGenerate = async () => {
    setRunning(true);
    setStatus("Generating...");

    try {
      const createRes = await fetch(`${API_BASE}/tasks`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: notes, type: "internal_generate" }),
      });

      if (!createRes.ok) {
        throw new Error(`Create failed: HTTP ${createRes.status}`);
      }

      const created: TaskCreateResponse = await createRes.json();
      const parentId = created.id;

      const runRes = await fetch(`${API_BASE}/tasks/${parentId}/run`, {
        method: "POST",
      });

      if (!runRes.ok) {
        throw new Error(`Run failed: HTTP ${runRes.status}`);
      }

      window.location.href = "/kanban";
    } catch (e) {
      const message = e instanceof Error ? e.message : "Unknown error";
      setStatus(`Error: ${message}`);
      setRunning(false);
    }
  };

  return (
    <main style={{ maxWidth: "900px", margin: "32px auto", padding: "0 16px" }}>
      <h1>Meeting → Execution Board</h1>
      <textarea
        placeholder="Paste meeting transcript or notes here..."
        rows={14}
        value={notes}
        onChange={(e) => setNotes(e.target.value)}
        style={{ width: "100%", marginTop: "16px", padding: "12px" }}
      />
      <div style={{ marginTop: "12px" }}>
        <button type="button" onClick={() => void onGenerate()} disabled={running}>
          Generate Kanban
        </button>
      </div>
      <div style={{ marginTop: "12px", minHeight: "24px" }}>{status}</div>
    </main>
  );
}
