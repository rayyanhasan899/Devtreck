"use client";
import { useEffect, useState } from "react";
import { Checklist } from "./checklist";
import { api, ApiError } from "@/services/api";
import { dateLabel, type Task, type History } from "./types";
export function TaskDetail({
  task,
  zone,
  onEdit,
}: {
  task: Task;
  zone: string;
  onEdit: () => void;
}) {
  const [history, setHistory] = useState<{
    once: History[];
    daily: History[];
  } | null>(null);
  const [offset, setOffset] = useState(0);
  const [error, setError] = useState("");
  useEffect(() => {
    let active = true;
    Promise.all([
      api<History[]>(`/tasks/${task.id}/history?limit=25&offset=${offset}`),
      api<History[]>(
        `/tasks/${task.id}/daily-history?limit=25&offset=${offset}`,
      ),
    ])
      .then(([once, daily]) => {
        if (active) setHistory({ once, daily });
      })
      .catch((e: ApiError) => {
        if (active) setError(e.message);
      });
    return () => {
      active = false;
    };
  }, [task.id, offset]);
  return (
    <>
      <p className="muted">
        {task.task_type === "daily" ? "Daily habit" : "One-time task"} ·{" "}
        {task.priority} priority
      </p>
      <p className="task-description">
        {task.description || "No description added."}
      </p>
      <p>
        {dateLabel(task, zone)} · {zone}
      </p>
      <p>
        {task.estimated_minutes
          ? `${task.estimated_minutes} estimated minutes`
          : "No duration estimate"}
      </p>
      {task.streak && (
        <p className="streak-banner">
          Current streak: {task.streak.current_streak} · Best streak:{" "}
          {task.streak.best_streak}
          <br />
          {task.streak.today_completed
            ? "Completed today"
            : "Today is still pending"}{" "}
          · {task.streak.total_completions} recorded days
        </p>
      )}
      <button className="secondary" onClick={onEdit}>
        Edit this task
      </button>
      <Checklist taskId={task.id} />
      <h3>Completion history</h3>
      {error && <p role="alert">{error}</p>}
      {!history && !error && <p role="status">Loading history…</p>}
      {history && (
        <>
          {history.once.length === 0 && history.daily.length === 0 && (
            <p>No completions recorded yet.</p>
          )}
          <ul className="history-list">
            {history.once.map((item) => (
              <li key={item.id}>
                One-time completion ·{" "}
                {new Intl.DateTimeFormat("en", {
                  dateStyle: "medium",
                  timeStyle: "short",
                  timeZone: zone,
                }).format(new Date(item.completed_at))}
              </li>
            ))}
            {history.daily.map((item) => (
              <li key={item.id}>
                Daily credit: {item.completion_day} · {item.time_zone}
                <small>
                  Recorded{" "}
                  {new Intl.DateTimeFormat("en", {
                    dateStyle: "medium",
                    timeStyle: "short",
                    timeZone: zone,
                  }).format(new Date(item.completed_at))}{" "}
                  ({zone})
                </small>
              </li>
            ))}
          </ul>
          <div className="pagination">
            <button
              className="secondary"
              disabled={offset === 0}
              onClick={() => {
                setHistory(null);
                setOffset(offset - 25);
              }}
            >
              Earlier page
            </button>
            <button
              className="secondary"
              disabled={history.once.length < 25 && history.daily.length < 25}
              onClick={() => {
                setHistory(null);
                setOffset(offset + 25);
              }}
            >
              More history
            </button>
          </div>
        </>
      )}
    </>
  );
}
