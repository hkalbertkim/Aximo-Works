"use client";

import { useEffect, useMemo, useRef, useState } from "react";

type TaskStatus = "pending_approval" | "approved" | "done";

type Task = {
  id: string;
  text: string;
  status: TaskStatus;
  parent_id: string | null;
  created_at: string;
  updated_at?: string | null;
  due_date?: string | null;
  owner?: string | null;
  priority?: "low" | "medium" | "high" | null;
  weight?: number | null;
  approved_at?: string | null;
  approved_by?: string | null;
  rejected_at?: string | null;
  rejected_by?: string | null;
  reject_reason?: string | null;
};

type ProxyHealthResponse = {
  ok: boolean;
  upstream_status?: number | null;
  error?: string;
};

const ARCHIVE_STORAGE_KEY = "aximo_archived_task_ids";
const ALERT_COOLDOWN_MS = 10 * 60 * 1000;
const ALERT_WEBHOOK =
  process.env.NEXT_PUBLIC_AXIMO_TELEGRAM_ALERT_WEBHOOK ||
  process.env.AXIMO_TELEGRAM_ALERT_WEBHOOK ||
  "";

const columns: Array<{ key: TaskStatus; title: string; barClass: string }> = [
  { key: "pending_approval", title: "Open", barClass: "bg-amber-400" },
  { key: "approved", title: "In Progress", barClass: "bg-sky-500" },
  { key: "done", title: "Done", barClass: "bg-emerald-500" },
];

const isTestTask = (text: string) => {
  return text.includes("CORS test") || text.startsWith("(Fallback)") || text.includes("Fallback");
};

const formatCreatedAt = (value: string) => {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleString(undefined, {
    month: "short",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
};

type DueSeverity = "overdue" | "due_soon" | "upcoming" | "no_due";
type PressureComputed = {
  timeScore: number;
  base: number;
  p2: number;
  bucket: DueSeverity;
  dueAt: Date | null;
};

const parseDateSafe = (value?: string | null): Date | null => {
  if (!value) return null;
  if (/^\d{4}-\d{2}-\d{2}$/.test(value)) {
    const [y, m, d] = value.split("-").map(Number);
    return new Date(y, m - 1, d, 23, 59, 59, 999);
  }
  const dt = new Date(value);
  return Number.isNaN(dt.getTime()) ? null : dt;
};

const getDueSeverity = (task: Task): { severity: DueSeverity; rank: number; dueAt: Date | null } => {
  const computed = computePressure(task, Date.now());
  const rank = computed.bucket === "overdue" ? 0 : computed.bucket === "due_soon" ? 1 : computed.bucket === "upcoming" ? 2 : 3;
  return { severity: computed.bucket, rank, dueAt: computed.dueAt };
};

const getTimeScore = (task: Task, nowMs: number): { timeScore: number; bucket: DueSeverity; dueAt: Date | null } => {
  const dueString = task.due_date;
  if (!dueString) return { timeScore: 0, bucket: "no_due", dueAt: null };

  const dueMs = Date.parse(dueString);
  if (Number.isNaN(dueMs)) return { timeScore: 0, bucket: "no_due", dueAt: null };

  const h24 = 24 * 60 * 60 * 1000;
  const h72 = 72 * 60 * 60 * 1000;
  const h = 60 * 60 * 1000;
  if (dueMs < nowMs) {
    return { timeScore: Math.min(999, 100 + Math.ceil((nowMs - dueMs) / h)), bucket: "overdue", dueAt: new Date(dueMs) };
  }
  if (nowMs <= dueMs && dueMs < nowMs + h24) {
    return { timeScore: Math.min(999, 50 + Math.ceil((h24 - (dueMs - nowMs)) / h)), bucket: "due_soon", dueAt: new Date(dueMs) };
  }
  if (nowMs + h24 <= dueMs && dueMs < nowMs + h72) {
    return { timeScore: Math.min(999, 10 + Math.ceil((h72 - (dueMs - nowMs)) / h)), bucket: "upcoming", dueAt: new Date(dueMs) };
  }
  return { timeScore: 0, bucket: "no_due", dueAt: new Date(dueMs) };
};

const normalizePriority = (priority?: string | null): "low" | "medium" | "high" => {
  if (priority === "low" || priority === "medium" || priority === "high") {
    return priority;
  }
  return "medium";
};

const clampWeight = (weight?: number | null): number => {
  const value = typeof weight === "number" && Number.isFinite(weight) ? weight : 1.0;
  if (value < 0.1) return 0.1;
  if (value > 10.0) return 10.0;
  return value;
};

const computePressure = (task: Task, nowMs: number): PressureComputed => {
  const { timeScore, bucket, dueAt } = getTimeScore(task, nowMs);
  const priority = normalizePriority(task.priority);
  const priorityFactor = priority === "high" ? 2.0 : priority === "low" ? 0.5 : 1.0;
  const base = clampWeight(task.weight) * priorityFactor;
  const p2 = Math.min(999, Math.max(0, Math.ceil(base * timeScore)));
  return { timeScore, base, p2, bucket, dueAt };
};

const isDoneOlderThan7Days = (task: Task, now = new Date()) => {
  if (task.status !== "done") return false;
  const ref = parseDateSafe(task.updated_at ?? task.created_at ?? task.due_date);
  if (!ref) return false;
  return ref.getTime() < now.getTime() - 7 * 24 * 60 * 60 * 1000;
};

const dueBadgeClass = (severity: DueSeverity) => {
  if (severity === "overdue") return "bg-rose-100 text-rose-700";
  if (severity === "due_soon") return "bg-orange-100 text-orange-700";
  if (severity === "upcoming") return "bg-amber-100 text-amber-700";
  return "";
};

const dueBadgeLabel = (severity: DueSeverity) => {
  if (severity === "overdue") return "Overdue";
  if (severity === "due_soon") return "Due Soon";
  if (severity === "upcoming") return "Upcoming";
  return "";
};

export default function KanbanPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showTestTasks, setShowTestTasks] = useState(false);
  const [groupByParent, setGroupByParent] = useState(true);
  const [archivedIds, setArchivedIds] = useState<Set<string>>(new Set());
  const [expandedParentIds, setExpandedParentIds] = useState<Set<string>>(new Set());
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [showArchivedPanel, setShowArchivedPanel] = useState(false);
  const [backendOk, setBackendOk] = useState(true);
  const [healthHint, setHealthHint] = useState("");
  const [actionErrors, setActionErrors] = useState<Record<string, string>>({});
  const lastAlertAtRef = useRef(0);
  const wasBackendOkRef = useRef(true);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }
    const saved = window.localStorage.getItem(ARCHIVE_STORAGE_KEY);
    if (!saved) {
      return;
    }
    try {
      const parsed = JSON.parse(saved);
      if (Array.isArray(parsed)) {
        setArchivedIds(new Set(parsed.filter((item): item is string => typeof item === "string")));
      }
    } catch {
      window.localStorage.removeItem(ARCHIVE_STORAGE_KEY);
    }
  }, []);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }
    window.localStorage.setItem(ARCHIVE_STORAGE_KEY, JSON.stringify(Array.from(archivedIds)));
  }, [archivedIds]);

  const sanitizeErrorText = (value: string) => value.replace(/[\r\n\t]+/g, " ").replace(/[^\x20-\x7E]/g, "").trim();

  const readErrorSnippet = async (res: Response) => {
    try {
      const body = sanitizeErrorText(await res.text());
      return body.slice(0, 200);
    } catch {
      return "";
    }
  };

  const fetchTasks = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await fetch("/api/proxy/tasks", {
        method: "GET",
        credentials: "include",
        cache: "no-store",
      });
      if (!res.ok) {
        const snippet = await readErrorSnippet(res);
        throw new Error(`HTTP ${res.status}${snippet ? `: ${snippet}` : ""}`);
      }
      const data: Task[] = await res.json();
      setTasks(data);
    } catch (e) {
      const message = e instanceof Error ? e.message : "Unknown error";
      setError(`Failed to load tasks: ${message}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void fetchTasks();
  }, []);

  const handleRetry = () => {
    void checkProxyHealth();
    void fetchTasks();
  };

  const checkProxyHealth = async () => {
    try {
      const res = await fetch("/api/proxy/health", {
        method: "GET",
        credentials: "include",
        cache: "no-store",
      });

      let payload: ProxyHealthResponse | null = null;
      try {
        payload = (await res.json()) as ProxyHealthResponse;
      } catch {
        payload = null;
      }

      if (!res.ok || !payload?.ok) {
        setBackendOk(false);
        const statusText = payload?.upstream_status != null ? `upstream_status=${payload.upstream_status}` : "upstream_status=unknown";
        const shortError = payload?.error ? sanitizeErrorText(payload.error).slice(0, 120) : "health check failed";
        setHealthHint(`${statusText} ${shortError}`.trim());
        return;
      }

      setBackendOk(true);
      setHealthHint("");
    } catch {
      setBackendOk(false);
      setHealthHint("upstream_status=unknown request failed");
    }
  };

  useEffect(() => {
    void checkProxyHealth();
    const timer = setInterval(() => {
      void checkProxyHealth();
    }, 30_000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    const turnedRed = !backendOk && wasBackendOkRef.current;
    const now = Date.now();
    if (!backendOk && ALERT_WEBHOOK && (turnedRed || now - lastAlertAtRef.current >= ALERT_COOLDOWN_MS)) {
      lastAlertAtRef.current = now;
      const payload = {
        text: "AXIMO Kanban backend issue detected",
        hint: healthHint || "unknown",
        ts: new Date(now).toISOString(),
      };
      void fetch(ALERT_WEBHOOK, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      }).catch(() => {});
    }
    wasBackendOkRef.current = backendOk;
  }, [backendOk, healthHint]);

  const visibleTasks = useMemo(() => {
    return tasks.filter((task) => {
      if (archivedIds.has(task.id)) {
        return false;
      }
      if (!showTestTasks && isTestTask(task.text)) {
        return false;
      }
      if (isDoneOlderThan7Days(task)) {
        return false;
      }
      return true;
    });
  }, [tasks, archivedIds, showTestTasks]);

  const tasksByStatus = useMemo(() => {
    const sorter = (a: Task, b: Task) => {
      const sa = getDueSeverity(a);
      const sb = getDueSeverity(b);
      if (sa.rank !== sb.rank) return sa.rank - sb.rank;
      if (sa.dueAt && sb.dueAt) return sa.dueAt.getTime() - sb.dueAt.getTime();
      if (sa.dueAt && !sb.dueAt) return -1;
      if (!sa.dueAt && sb.dueAt) return 1;
      const ac = parseDateSafe(a.created_at)?.getTime() ?? 0;
      const bc = parseDateSafe(b.created_at)?.getTime() ?? 0;
      return bc - ac;
    };
    return {
      pending_approval: visibleTasks.filter((t) => t.status === "pending_approval").sort(sorter),
      approved: visibleTasks.filter((t) => t.status === "approved").sort(sorter),
      done: visibleTasks.filter((t) => t.status === "done").sort(sorter),
    };
  }, [visibleTasks]);

  const archivedTasks = useMemo(() => {
    return tasks.filter((task) => archivedIds.has(task.id) || isDoneOlderThan7Days(task));
  }, [tasks, archivedIds]);

  useEffect(() => {
    const parentIds = new Set(visibleTasks.filter((task) => task.parent_id == null).map((task) => task.id));
    setExpandedParentIds(parentIds);
  }, [visibleTasks]);

  const updateStatus = async (taskId: string, status: TaskStatus) => {
    try {
      const res = await fetch(`/api/proxy/tasks/${taskId}/status`, {
        method: "POST",
        credentials: "include",
        cache: "no-store",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status }),
      });
      if (!res.ok) {
        const snippet = await readErrorSnippet(res);
        throw new Error(`HTTP ${res.status}${snippet ? `: ${snippet}` : ""}`);
      }
      await fetchTasks();
    } catch (e) {
      const message = e instanceof Error ? e.message : "Unknown error";
      setError(`Failed to update status: ${message}`);
    }
  };

  const approveTask = async (taskId: string) => {
    setActionErrors((prev) => ({ ...prev, [taskId]: "" }));
    try {
      const res = await fetch(`/api/proxy/tasks/${taskId}/approve`, {
        method: "POST",
        credentials: "include",
        cache: "no-store",
      });
      if (!res.ok) {
        const snippet = await readErrorSnippet(res);
        throw new Error(`HTTP ${res.status}${snippet ? `: ${snippet}` : ""}`);
      }
      await fetchTasks();
    } catch (e) {
      const message = e instanceof Error ? e.message : "Unknown error";
      setActionErrors((prev) => ({ ...prev, [taskId]: `Approve failed: ${message}` }));
    }
  };

  const rejectTask = async (taskId: string) => {
    const reason = window.prompt("Reject reason (optional):", "") ?? null;
    if (reason === null) return;
    setActionErrors((prev) => ({ ...prev, [taskId]: "" }));
    try {
      const res = await fetch(`/api/proxy/tasks/${taskId}/reject`, {
        method: "POST",
        credentials: "include",
        cache: "no-store",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ reason }),
      });
      if (!res.ok) {
        const snippet = await readErrorSnippet(res);
        throw new Error(`HTTP ${res.status}${snippet ? `: ${snippet}` : ""}`);
      }
      await fetchTasks();
    } catch (e) {
      const message = e instanceof Error ? e.message : "Unknown error";
      setActionErrors((prev) => ({ ...prev, [taskId]: `Reject failed: ${message}` }));
    }
  };

  const archiveTask = (taskId: string) => {
    setArchivedIds((prev) => {
      const next = new Set(prev);
      next.add(taskId);
      return next;
    });
    setSelectedTask((prev) => (prev?.id === taskId ? null : prev));
  };

  const unarchiveTask = (taskId: string) => {
    setArchivedIds((prev) => {
      const next = new Set(prev);
      next.delete(taskId);
      return next;
    });
  };

  const toggleParentExpanded = (taskId: string) => {
    setExpandedParentIds((prev) => {
      const next = new Set(prev);
      if (next.has(taskId)) {
        next.delete(taskId);
      } else {
        next.add(taskId);
      }
      return next;
    });
  };

  const renderTaskCard = (
    task: Task,
    barClass: string,
    columnKey: TaskStatus,
    isParentExpanded: boolean,
    canToggleParent: boolean,
    depth = 0,
    grouped = false
  ) => {
    const isChild = task.parent_id != null;
    const isPendingApproval = task.status === "pending_approval";
    const isApproved = task.status === "approved";
    const due = getDueSeverity(task);
    const dueClass = dueBadgeClass(due.severity);
    const dueLabel = dueBadgeLabel(due.severity);
    const pressure = computePressure(task, Date.now());
    const isOverdue = due.severity === "overdue";
    const priority = normalizePriority(task.priority);
    const weight = clampWeight(task.weight);

    return (
      <div key={task.id} className={grouped ? "space-y-2" : ""}>
        <article
          role="button"
          tabIndex={0}
          onClick={() => setSelectedTask(task)}
          onKeyDown={(event) => {
            if (event.key === "Enter" || event.key === " ") {
              event.preventDefault();
              setSelectedTask(task);
            }
          }}
          className={`group relative cursor-pointer overflow-hidden rounded-xl border bg-white/95 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md ${
            isOverdue
              ? "border-rose-300 bg-rose-50/40"
              : isChild
                ? "border-slate-200"
                : "border-slate-300"
          }`}
          style={{ marginLeft: grouped ? depth * 16 : 0 }}
        >
          <div className={`absolute inset-y-0 left-0 ${isOverdue ? "w-2.5 bg-rose-500" : `w-1.5 ${barClass}`}`} />
          <div className="space-y-3 p-4 pl-5">
            <div className="flex items-start justify-between gap-2">
              <p className={`line-clamp-3 text-sm ${isChild ? "font-medium text-slate-700" : "font-semibold text-slate-900"}`}>
                {task.text}
              </p>
              <div className="flex shrink-0 items-center gap-2">
                <span
                  className={`rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide ${
                    isChild ? "bg-indigo-100 text-indigo-700" : "bg-slate-200 text-slate-700"
                  }`}
                >
                  {isChild ? "Child" : "Parent"}
                </span>
                {grouped && canToggleParent ? (
                  <button
                    type="button"
                    onClick={(event) => {
                      event.stopPropagation();
                      toggleParentExpanded(task.id);
                    }}
                    className="rounded-md border border-slate-300 bg-white px-2 py-0.5 text-[10px] font-medium text-slate-600 transition hover:bg-slate-100"
                  >
                    {isParentExpanded ? "Collapse" : "Expand"}
                  </button>
                ) : null}
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-2 text-xs text-slate-500">
              <span className="rounded bg-slate-100 px-2 py-0.5 font-mono">{task.id.slice(0, 8)}</span>
              <span>{formatCreatedAt(task.created_at)}</span>
              <span className="rounded bg-slate-800 px-2 py-0.5 text-white">P:{pressure.p2}</span>
              {task.due_date ? <span className="rounded bg-slate-100 px-2 py-0.5">Due: {task.due_date}</span> : null}
              {dueLabel ? <span className={`rounded px-2 py-0.5 ${dueClass}`}>{dueLabel}</span> : null}
            </div>
            <div className="text-xs text-slate-500">
              {task.owner ? <span className="mr-2">Owner: {task.owner}</span> : null}
              <span>
                prio:{priority} w:{weight}
              </span>
              {task.text.startsWith("[DEMO] Due Soon") ? (
                <span className="ml-2 text-slate-400">
                  ts:{pressure.timeScore} base:{pressure.base.toFixed(2)} p2:{pressure.p2}
                </span>
              ) : null}
            </div>
            {isApproved && task.approved_at ? (
              <div className="text-xs text-slate-400">
                Approved by {task.approved_by || "admin"} at {formatCreatedAt(task.approved_at)}
              </div>
            ) : null}
            {task.reject_reason ? (
              <div className="text-xs text-rose-600">
                Rejected by {task.rejected_by || "admin"}: {task.reject_reason}
              </div>
            ) : null}

            <div className="flex flex-wrap gap-2 pt-1">
              {isPendingApproval ? (
                <>
                  <button
                    type="button"
                    onClick={(event) => {
                      event.stopPropagation();
                      void approveTask(task.id);
                    }}
                    className="rounded-md bg-emerald-600 px-2.5 py-1 text-xs font-medium text-white transition hover:bg-emerald-700"
                  >
                    Approve
                  </button>
                  <button
                    type="button"
                    onClick={(event) => {
                      event.stopPropagation();
                      void rejectTask(task.id);
                    }}
                    className="rounded-md bg-rose-600 px-2.5 py-1 text-xs font-medium text-white transition hover:bg-rose-700"
                  >
                    Reject
                  </button>
                </>
              ) : null}
              {columnKey !== "done" && !isPendingApproval ? (
                <>
                  <button
                    type="button"
                    onClick={(event) => {
                      event.stopPropagation();
                      void updateStatus(task.id, "approved");
                    }}
                    className="rounded-md bg-sky-600 px-2.5 py-1 text-xs font-medium text-white transition hover:bg-sky-700"
                  >
                    Mark In Progress
                  </button>
                  <button
                    type="button"
                    onClick={(event) => {
                      event.stopPropagation();
                      void updateStatus(task.id, "done");
                    }}
                    className="rounded-md bg-emerald-600 px-2.5 py-1 text-xs font-medium text-white transition hover:bg-emerald-700"
                  >
                    Mark Done
                  </button>
                </>
              ) : null}
              <button
                type="button"
                onClick={(event) => {
                  event.stopPropagation();
                  archiveTask(task.id);
                }}
                className="rounded-md bg-slate-700 px-2.5 py-1 text-xs font-medium text-white transition hover:bg-slate-800"
              >
                Archive
              </button>
            </div>
            {actionErrors[task.id] ? <div className="text-xs text-rose-600">{actionErrors[task.id]}</div> : null}
          </div>
        </article>
      </div>
    );
  };

  const renderTaskTree = (
    task: Task,
    inColumn: Task[],
    barClass: string,
    columnKey: TaskStatus,
    depth = 0
  ) => {
    const children = inColumn.filter((candidate) => candidate.parent_id === task.id);
    const canToggleParent = task.parent_id == null;
    const isParentExpanded = canToggleParent ? expandedParentIds.has(task.id) : true;
    return (
      <div key={task.id} className="space-y-2">
        {renderTaskCard(task, barClass, columnKey, isParentExpanded, canToggleParent, depth, true)}
        {isParentExpanded ? children.map((child) => renderTaskTree(child, inColumn, barClass, columnKey, depth + 1)) : null}
      </div>
    );
  };

  return (
    <main className="min-h-screen bg-slate-100 p-4 md:p-8">
      <div className="mx-auto flex w-full max-w-7xl flex-col gap-5">
        <header className="rounded-2xl bg-slate-900 px-5 py-4 text-slate-100 shadow-panel">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div>
              <h1 className="text-xl font-semibold tracking-tight">Kanban Board</h1>
              <p className="text-sm text-slate-300">Operational task flow with parent and child tracking</p>
            </div>
            <div className="flex flex-wrap items-center gap-3">
              <div className="flex items-center gap-2">
                <span
                  className={`rounded-full px-2.5 py-1 text-xs font-semibold ${
                    backendOk ? "bg-emerald-100 text-emerald-800" : "bg-rose-100 text-rose-800"
                  }`}
                  title={backendOk ? "Proxy health is normal" : healthHint || "Backend issue detected"}
                >
                  {backendOk ? "Backend OK" : "Backend Issue"}
                </span>
                <button
                  type="button"
                  onClick={handleRetry}
                  className="rounded-md bg-slate-100 px-3 py-1.5 text-sm font-medium text-slate-900 transition hover:bg-white"
                >
                  Retry
                </button>
              </div>
              <button
                type="button"
                onClick={() => void fetchTasks()}
                className="rounded-md bg-slate-100 px-3 py-1.5 text-sm font-medium text-slate-900 transition hover:bg-white"
              >
                Refresh
              </button>
              <button
                type="button"
                onClick={() => setShowArchivedPanel(true)}
                className="rounded-md bg-slate-100 px-3 py-1.5 text-sm font-medium text-slate-900 transition hover:bg-white"
              >
                Archived
              </button>

              <label className="inline-flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={showTestTasks}
                  onChange={(event) => setShowTestTasks(event.target.checked)}
                  className="h-4 w-4 rounded border-slate-300 text-sky-500 focus:ring-sky-500"
                />
                Show test tasks
              </label>

              <label className="inline-flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={groupByParent}
                  onChange={(event) => setGroupByParent(event.target.checked)}
                  className="h-4 w-4 rounded border-slate-300 text-sky-500 focus:ring-sky-500"
                />
                Group by parent
              </label>
              <span className="text-xs text-slate-300">v:cf27283</span>
            </div>
          </div>
          {!backendOk ? (
            <div className="mt-2 flex items-center justify-between gap-3 rounded-lg border border-rose-300 bg-rose-100/20 px-3 py-2">
              <p className="text-xs text-rose-100">
                Backend Issue — tasks may be stale
                {healthHint ? ` (${healthHint})` : ""}
              </p>
              <button
                type="button"
                onClick={handleRetry}
                className="shrink-0 rounded-md border border-rose-300 bg-white px-2.5 py-1 text-xs font-medium text-rose-700 transition hover:bg-rose-100"
              >
                Retry
              </button>
            </div>
          ) : null}
        </header>

        {loading ? <p className="text-sm text-slate-600">Loading...</p> : null}
        {error ? (
          <div className="flex items-center justify-between gap-3 rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">
            <p>{error}</p>
            <button
              type="button"
              onClick={() => void fetchTasks()}
              className="shrink-0 rounded-md border border-rose-300 bg-white px-2.5 py-1 text-xs font-medium text-rose-700 transition hover:bg-rose-100"
            >
              Retry
            </button>
          </div>
        ) : null}

        <div className="relative">
          <div className={`grid gap-4 md:grid-cols-3 ${backendOk ? "" : "pointer-events-none opacity-70"}`}>
            {columns.map((column) => {
              const inColumn = tasksByStatus[column.key];
              const pressureTotal = inColumn.reduce((sum, task) => sum + computePressure(task, Date.now()).p2, 0);
              const parents = inColumn.filter((task) => task.parent_id == null);
              const orphanChildren = inColumn.filter(
                (task) => task.parent_id != null && !inColumn.some((candidate) => candidate.id === task.parent_id)
              );

              return (
                <section key={column.key} className="rounded-2xl border border-slate-200 bg-slate-50 p-3 shadow-sm">
                  <div className="mb-3 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-700">{column.title}</h2>
                      <span className="rounded-full bg-slate-200 px-2 py-0.5 text-xs font-semibold text-slate-700">
                        Pressure:{pressureTotal}
                      </span>
                    </div>
                    <span className="rounded-full bg-white px-2 py-0.5 text-xs font-medium text-slate-500">{inColumn.length}</span>
                  </div>

                  <div className="space-y-2">
                    {groupByParent
                      ? (
                          <>
                            {parents.map((task) => renderTaskTree(task, inColumn, column.barClass, column.key))}
                            {orphanChildren.map((task) => renderTaskTree(task, inColumn, column.barClass, column.key, 1))}
                          </>
                        )
                      : inColumn.map((task) => renderTaskCard(task, column.barClass, column.key, true, false))}
                    {!inColumn.length ? (
                      <div className="rounded-lg border border-dashed border-slate-300 bg-white px-3 py-6 text-center text-xs text-slate-500">
                        No tasks
                      </div>
                    ) : null}
                  </div>
                </section>
              );
            })}
          </div>
          {!backendOk ? <div className="pointer-events-none absolute inset-0 rounded-2xl bg-slate-900/10" /> : null}
        </div>
      </div>

      {selectedTask ? (
        <div className="fixed inset-0 z-50 flex justify-end bg-slate-900/40" onClick={() => setSelectedTask(null)}>
          <aside
            className="h-full w-full max-w-md overflow-y-auto bg-white p-6 shadow-2xl"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="mb-4 flex items-center justify-between">
              <h3 className="text-lg font-semibold text-slate-900">Task details</h3>
              <button
                type="button"
                onClick={() => setSelectedTask(null)}
                className="rounded-md border border-slate-300 px-2 py-1 text-sm text-slate-600 transition hover:bg-slate-100"
              >
                Close
              </button>
            </div>

            <div className="space-y-4 text-sm text-slate-700">
              <div>
                <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-500">Text</p>
                <p className="rounded-lg bg-slate-100 p-3 leading-relaxed">{selectedTask.text}</p>
              </div>
              <div>
                <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-500">ID</p>
                <p className="font-mono text-xs">{selectedTask.id}</p>
              </div>
              <div>
                <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-500">Status</p>
                <p>{selectedTask.status}</p>
              </div>
              <div>
                <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-500">Parent ID</p>
                <p className="font-mono text-xs">{selectedTask.parent_id ?? "None"}</p>
              </div>
              <div>
                <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-500">Created At</p>
                <p>{selectedTask.created_at}</p>
              </div>
              {selectedTask.due_date ? (
                <div>
                  <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-500">Due Date</p>
                  <p>{selectedTask.due_date}</p>
                </div>
              ) : null}
            </div>
          </aside>
        </div>
      ) : null}

      {showArchivedPanel ? (
        <div className="fixed inset-0 z-50 flex justify-end bg-slate-900/40" onClick={() => setShowArchivedPanel(false)}>
          <aside
            className="h-full w-full max-w-md overflow-y-auto bg-white p-6 shadow-2xl"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="mb-4 flex items-center justify-between">
              <h3 className="text-lg font-semibold text-slate-900">Archived tasks</h3>
              <button
                type="button"
                onClick={() => setShowArchivedPanel(false)}
                className="rounded-md border border-slate-300 px-2 py-1 text-sm text-slate-600 transition hover:bg-slate-100"
              >
                Close
              </button>
            </div>

            {archivedTasks.length ? (
              <div className="space-y-2">
                {archivedTasks.map((task) => (
                  <div key={task.id} className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                    <div className="flex items-start justify-between gap-3">
                      <div className="min-w-0 space-y-1">
                        <p className="truncate text-sm font-medium text-slate-900">{task.text}</p>
                        <div className="flex items-center gap-2 text-xs text-slate-500">
                          <span className="rounded bg-white px-2 py-0.5 font-mono">{task.id.slice(0, 8)}</span>
                          {isDoneOlderThan7Days(task) ? (
                            <span className="rounded-full bg-slate-200 px-2 py-0.5 font-semibold uppercase tracking-wide text-slate-700">
                              Done &gt; 7d
                            </span>
                          ) : null}
                          <span
                            className={`rounded-full px-2 py-0.5 font-semibold uppercase tracking-wide ${
                              task.status === "pending_approval"
                                ? "bg-amber-100 text-amber-700"
                                : task.status === "approved"
                                  ? "bg-sky-100 text-sky-700"
                                  : "bg-emerald-100 text-emerald-700"
                            }`}
                          >
                            {task.status}
                          </span>
                        </div>
                      </div>
                      {archivedIds.has(task.id) ? (
                        <button
                          type="button"
                          onClick={() => unarchiveTask(task.id)}
                          className="shrink-0 rounded-md bg-slate-700 px-2.5 py-1 text-xs font-medium text-white transition hover:bg-slate-800"
                        >
                          Unarchive
                        </button>
                      ) : null}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="rounded-lg border border-dashed border-slate-300 bg-slate-50 px-3 py-6 text-center text-sm text-slate-500">
                No archived tasks
              </p>
            )}
          </aside>
        </div>
      ) : null}
    </main>
  );
}
