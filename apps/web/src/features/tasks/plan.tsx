"use client";
import { useEffect, useState, useRef } from "react";
import Link from "next/link";
import { api, ApiError } from "@/services/api";
import type { Task } from "./types";
type Plan = {
  day: string;
  time_zone: string;
  items: Task[];
  priority_ids: string[];
  suggested_ids: string[];
  estimated_minutes: number;
  missing_estimates: number;
  truncated: boolean;
  total: number;
  reasons: Record<string, string[]>;
};
export function DailyPlan() {
  const [plan, setPlan] = useState<Plan | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const guard = useRef(false);
  const [tick, setTick] = useState(0);
  useEffect(() => {
    let active = true;
    api<Plan>("/plan/today")
      .then((value) => {
        if (active) setPlan(value);
      })
      .catch((e: ApiError) => {
        if (active) setError(e.message);
      });
    const refresh = () => setTick((value) => value + 1);
    window.addEventListener("focus", refresh);
    const timer = setInterval(refresh, 60000);
    return () => {
      active = false;
      window.removeEventListener("focus", refresh);
      clearInterval(timer);
    };
  }, [tick]);
  async function save(ids: string[], priorities: string[]) {
    if (guard.current) return;
    guard.current = true;
    setBusy(true);
    setError("");
    try {
      await api("/plan/today", {
        method: "PUT",
        body: JSON.stringify({ order_ids: ids, priority_ids: priorities }),
      });
      setPlan(await api<Plan>("/plan/today"));
    } catch (e) {
      setError((e as ApiError).message);
    } finally {
      setBusy(false);
      guard.current = false;
    }
  }
  return (
    <section
      className="settings-card daily-plan"
      aria-labelledby="plan-heading"
    >
      <div className="dialog-heading">
        <h2 id="plan-heading">Your daily plan</h2>
        <Link href="/app">Manage today’s tasks</Link>
      </div>
      <p className="muted">
        Choose up to three priorities and arrange your day. Suggestions consider
        deadlines, priority and duration.
      </p>
      {error && (
        <p role="alert">
          {error}
          <button
            className="text-button"
            onClick={() => {
              setError("");
              setTick((value) => value + 1);
            }}
          >
            Retry
          </button>
        </p>
      )}
      {!plan && !error && <p role="status">Loading your plan…</p>}
      {plan && (
        <>
          <p>
            {plan.day} · {plan.time_zone} · Approximately{" "}
            {plan.estimated_minutes} min estimated
            {plan.missing_estimates > 0
              ? ` + ${plan.missing_estimates} tasks without estimates`
              : ""}
          </p>
          {plan.truncated && (
            <p>
              Showing the first 500 of {plan.total} tasks. Workload estimate
              covers shown tasks only.
            </p>
          )}
          {plan.items.length === 0 && (
            <p>No actionable tasks today. Add a task or habit in Today.</p>
          )}
          <ol className="plan-items">
            {plan.items.map((task, index) => {
              const selected = plan.priority_ids.includes(task.id);
              return (
                <li key={task.id}>
                  <div>
                    <strong>{task.title}</strong>
                    <small>
                      {plan.reasons[task.id]?.join(" · ") || "Available today"}
                    </small>
                  </div>
                  <div className="mini-actions">
                    <button
                      className={selected ? "primary" : "secondary"}
                      aria-pressed={selected}
                      disabled={
                        busy || (!selected && plan.priority_ids.length >= 3)
                      }
                      onClick={() =>
                        void save(
                          plan.items.map((item) => item.id),
                          selected
                            ? plan.priority_ids.filter((id) => id !== task.id)
                            : [...plan.priority_ids, task.id],
                        )
                      }
                    >
                      {selected ? "Top priority" : "Make priority"}
                      <span className="sr-only"> {task.title}</span>
                    </button>
                    <button
                      className="secondary"
                      aria-label={`Move ${task.title} up`}
                      disabled={busy || index === 0}
                      onClick={() => {
                        const ids = plan.items.map((item) => item.id);
                        [ids[index], ids[index - 1]] = [
                          ids[index - 1],
                          ids[index],
                        ];
                        void save(ids, plan.priority_ids);
                      }}
                    >
                      ↑
                    </button>
                    <button
                      className="secondary"
                      aria-label={`Move ${task.title} down`}
                      disabled={busy || index === plan.items.length - 1}
                      onClick={() => {
                        const ids = plan.items.map((item) => item.id);
                        [ids[index], ids[index + 1]] = [
                          ids[index + 1],
                          ids[index],
                        ];
                        void save(ids, plan.priority_ids);
                      }}
                    >
                      ↓
                    </button>
                  </div>
                </li>
              );
            })}
          </ol>
          {plan.items.length > 0 && (
            <button
              className="text-button"
              disabled={busy}
              onClick={() => void save([], plan.priority_ids)}
            >
              Use suggested order
            </button>
          )}
        </>
      )}
    </section>
  );
}
