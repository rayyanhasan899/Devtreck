"use client";
import { useEffect, useRef, useState } from "react";
import { api, ApiError } from "@/services/api";
import type { TaskPage } from "@/features/tasks/types";
type Session = {
  id: string;
  task_id: string | null;
  kind: string;
  status: string;
  target_seconds: number;
  elapsed_seconds: number;
  started_at: string;
  ended_at: string | null;
  server_now: string;
};
type Totals = {
  day_seconds: number;
  week_seconds: number;
  day: string;
  week_start: string;
  time_zone: string;
};
const duration = (seconds: number) =>
  `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, "0")}`;
export function Focus() {
  const [current, setCurrent] = useState<Session | null>(null);
  const [history, setHistory] = useState<Session[]>([]);
  const [totals, setTotals] = useState<Totals | null>(null);
  const [tasks, setTasks] = useState<TaskPage | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [seconds, setSeconds] = useState(0);
  const [focusMinutes, setFocusMinutes] = useState(25);
  const [breakMinutes, setBreakMinutes] = useState(5);
  const [kind, setKind] = useState("focus");
  const [offset, setOffset] = useState(0);
  const guard = useRef(false);
  const pending = useRef<Record<string, string>>({});
  const sampled = useRef(0);
  const version = useRef(0);
  async function refresh() {
    const sequence = ++version.current;
    const [active, past, total, options] = await Promise.all([
      api<Session | null>("/focus/current"),
      api<Session[]>(`/focus/history?limit=10&offset=${offset}`),
      api<Totals>("/focus/summary"),
      api<TaskPage>("/tasks?limit=100"),
    ]);
    if (sequence !== version.current) return;
    sampled.current = performance.now();
    setCurrent(active);
    setHistory(past);
    setTotals(total);
    setTasks(options);
    setLoading(false);
  }
  useEffect(() => {
    let active = true;
    const load = () => {
      const sequence = ++version.current;
      void Promise.all([
        api<Session | null>("/focus/current"),
        api<Session[]>(`/focus/history?limit=10&offset=${offset}`),
        api<Totals>("/focus/summary"),
        api<TaskPage>("/tasks?limit=100"),
      ])
        .then(([session, past, total, options]) => {
          if (active && sequence === version.current) {
            sampled.current = performance.now();
            setCurrent(session);
            setHistory(past);
            setTotals(total);
            setTasks(options);
            setLoading(false);
          }
        })
        .catch((e: ApiError) => {
          if (active && sequence === version.current) {
            setError(e.message);
            setLoading(false);
          }
        });
    };
    load();
    window.addEventListener("focus", load);
    const poll = setInterval(load, 3000);
    return () => {
      active = false;
      window.removeEventListener("focus", load);
      clearInterval(poll);
    };
  }, [offset]);
  useEffect(() => {
    const tick = () =>
      setSeconds(
        current
          ? Math.min(
              current.target_seconds,
              Math.floor(
                current.elapsed_seconds +
                  (current.status === "active"
                    ? (performance.now() - sampled.current) / 1000
                    : 0),
              ),
            )
          : 0,
      );
    const timer = setInterval(tick, 250);
    return () => clearInterval(timer);
  }, [current]);
  async function command(action: string, taskId?: string) {
    if (guard.current) return;
    guard.current = true;
    setBusy(true);
    setError("");
    const scope = action + ":" + (current?.id ?? "start");
    const key = pending.current[scope] ?? crypto.randomUUID();
    pending.current[scope] = key;
    try {
      await api(
        action === "start" ? "/focus" : `/focus/${current?.id}/${action}`,
        {
          method: "POST",
          body: JSON.stringify(
            action === "start"
              ? {
                  key,
                  task_id: taskId || null,
                  kind,
                  seconds:
                    (kind === "focus" ? focusMinutes : breakMinutes) * 60,
                }
              : { key },
          ),
        },
      );
      delete pending.current[scope];
      await refresh();
    } catch (e) {
      setError((e as ApiError).message);
    } finally {
      guard.current = false;
      setBusy(false);
    }
  }
  return (
    <main id="main" className="workspace-main">
      <p className="eyebrow">ONE THING AT A TIME</p>
      <h1>Focus</h1>
      <p className="intro">
        Give your work a little space. Sessions are saved across navigation and
        refresh.
      </p>
      {error && (
        <p className="notice error" role="alert">
          {error}
        </p>
      )}
      {loading && <p role="status">Loading focus sessions…</p>}
      {!loading && (
        <>
          <section className="settings-card focus-card">
            <p className="eyebrow">
              {current
                ? current.kind === "break"
                  ? "BREAK SESSION"
                  : "FOCUS SESSION"
                : "READY WHEN YOU ARE"}
            </p>
            <div className="timer" role="timer" aria-label="Time remaining">
              {current
                ? duration(Math.max(0, current.target_seconds - seconds))
                : duration(
                    (kind === "focus" ? focusMinutes : breakMinutes) * 60,
                  )}
            </div>
            <p>
              {current
                ? current.status === "paused"
                  ? "Paused — take your time."
                  : "In progress. Your time is recorded on the server."
                : "Choose a session and begin."}
            </p>
            {current ? (
              <div className="dialog-actions">
                <button
                  className="primary"
                  disabled={busy}
                  onClick={() =>
                    void command(
                      current.status === "paused" ? "resume" : "pause",
                    )
                  }
                >
                  {current.status === "paused" ? "Resume" : "Pause"}
                </button>
                <button
                  className="secondary"
                  disabled={busy}
                  onClick={() => void command("stop")}
                >
                  Stop session
                </button>
              </div>
            ) : (
              <form
                onSubmit={(event) => {
                  event.preventDefault();
                  void command(
                    "start",
                    String(
                      new FormData(event.currentTarget).get("task_id") || "",
                    ),
                  );
                }}
              >
                <div className="editor-grid">
                  <label>
                    Focus minutes
                    <input
                      type="number"
                      min={1}
                      max={180}
                      required
                      value={focusMinutes}
                      onChange={(e) => setFocusMinutes(Number(e.target.value))}
                    />
                  </label>
                  <label>
                    Break minutes
                    <input
                      type="number"
                      min={1}
                      max={60}
                      required
                      value={breakMinutes}
                      onChange={(e) => setBreakMinutes(Number(e.target.value))}
                    />
                  </label>
                </div>
                <label>
                  Session type
                  <select
                    aria-label="Session type"
                    value={kind}
                    onChange={(e) => setKind(e.target.value)}
                  >
                    <option value="focus">Focus</option>
                    <option value="break">Break</option>
                  </select>
                </label>
                <label>
                  Associated task
                  <select aria-label="Associated task" name="task_id">
                    <option value="">General focus</option>
                    {tasks?.items.map((task) => (
                      <option value={task.id} key={task.id}>
                        {task.title}
                      </option>
                    ))}
                  </select>
                  <small>
                    First 100 active tasks shown. A session never automatically
                    completes a task.
                  </small>
                </label>
                <button className="primary" disabled={busy}>
                  {busy
                    ? "Starting…"
                    : kind === "focus"
                      ? "Start focus"
                      : "Start break"}
                </button>
              </form>
            )}
          </section>
          {totals && (
            <section className="summary-grid" aria-label="Focus summary">
              <div>
                <span>Focus today</span>
                <strong>{Math.floor(totals.day_seconds / 60)} min</strong>
                <small>{totals.day}</small>
              </div>
              <div>
                <span>Last seven days</span>
                <strong>{Math.floor(totals.week_seconds / 60)} min</strong>
                <small>
                  {totals.week_start} through {totals.day} · {totals.time_zone}
                </small>
              </div>
            </section>
          )}
          <section className="settings-card">
            <h2>Session history</h2>
            <p className="muted">
              Only active focus intervals contribute to focus time. Pauses and
              breaks are excluded.
            </p>
            {history.length === 0 && (
              <p>No sessions yet. Your first one starts here.</p>
            )}
            <ul className="focus-history">
              {history.map((session) => (
                <li key={session.id}>
                  <strong>
                    {session.kind === "break" ? "Break" : "Focus"} ·{" "}
                    {session.status}
                  </strong>
                  <span>{duration(session.elapsed_seconds)} active time</span>
                  <small>
                    {new Intl.DateTimeFormat("en", {
                      dateStyle: "medium",
                      timeStyle: "short",
                      timeZone: totals?.time_zone ?? "UTC",
                    }).format(new Date(session.started_at))}
                  </small>
                </li>
              ))}
            </ul>
            <div className="pagination">
              <button
                className="secondary"
                disabled={offset === 0}
                onClick={() => setOffset(offset - 10)}
              >
                Previous sessions
              </button>
              <button
                className="secondary"
                disabled={history.length < 10}
                onClick={() => setOffset(offset + 10)}
              >
                More sessions
              </button>
            </div>
          </section>
        </>
      )}
    </main>
  );
}
