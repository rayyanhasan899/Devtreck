"use client";
import { useRef, useState } from "react";
import { api, ApiError } from "@/services/api";
import type { Category, Task } from "./types";

export function TaskEditor({
  task,
  categories,
  onSaved,
  onCancel,
}: {
  task?: Task;
  categories: Category[];
  onSaved: () => void;
  onCancel: () => void;
}) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);
  const guard = useRef(false);
  const [deadline, setDeadline] = useState(
    task?.due_at ? "timed" : task?.due_date ? "date" : "none",
  );
  const invalid = (name: string) =>
    error?.fields.some((field) => field.split(".").includes(name));
  async function save(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (guard.current) return;
    guard.current = true;
    setBusy(true);
    setError(null);
    const data = new FormData(event.currentTarget);
    try {
      const body = {
        title: String(data.get("title")).trim(),
        description: String(data.get("description") || "") || null,
        task_type: data.get("task_type"),
        priority: data.get("priority"),
        category_id: data.get("category_id") || null,
        estimated_minutes: data.get("estimated_minutes")
          ? Number(data.get("estimated_minutes"))
          : null,
        due_date: deadline === "date" ? data.get("due_date") : null,
        due_at:
          deadline === "timed"
            ? new Date(String(data.get("due_at"))).toISOString()
            : null,
        ...(task && data.get("status") !== "completed"
          ? { status: data.get("status") }
          : {}),
      };
      await api(task ? `/tasks/${task.id}` : "/tasks", {
        method: task ? "PATCH" : "POST",
        body: JSON.stringify(body),
      });
      onSaved();
    } catch (e) {
      setError(
        e instanceof ApiError
          ? e
          : new ApiError(422, "Please check your deadline."),
      );
    } finally {
      setBusy(false);
      guard.current = false;
    }
  }
  return (
    <form onSubmit={save} aria-busy={busy}>
      <fieldset disabled={busy}>
        <label>
          Task title
          <input
            name="title"
            aria-label="Task title"
            defaultValue={task?.title}
            required
            maxLength={200}
            aria-invalid={!!invalid("title")}
            autoFocus
          />
          {invalid("title") && (
            <small>Enter a nonblank title (up to 200 characters).</small>
          )}
        </label>
        <label>
          Description
          <textarea
            name="description"
            defaultValue={task?.description ?? ""}
            maxLength={10000}
            rows={3}
          />
        </label>
        <div className="editor-grid">
          <label>
            Task type
            <select
              name="task_type"
              defaultValue={task?.task_type ?? "one-time"}
            >
              <option value="one-time">One-time task</option>
              <option value="daily">Daily habit</option>
            </select>
          </label>
          <label>
            Priority
            <select
              aria-label="Priority"
              name="priority"
              defaultValue={task?.priority ?? "medium"}
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
          </label>
        </div>
        {task && (
          <label>
            Work status
            <select
              aria-label="Work status"
              name="status"
              defaultValue={task.status}
            >
              <option value="pending">Pending</option>
              <option value="in-progress">In progress</option>
              {task.status === "completed" && (
                <option value="completed">Completed</option>
              )}
            </select>
            <small>
              Use Complete in the task list to record completion. Changing type
              starts a new daily run; history remains.
            </small>
          </label>
        )}
        <div className="editor-grid">
          <label>
            Category
            <select
              aria-label="Category"
              name="category_id"
              defaultValue={task?.category_id ?? ""}
            >
              <option value="">Uncategorized</option>
              {task?.category_id &&
                !categories.some(
                  (category) => category.id === task.category_id,
                ) && (
                  <option value={task.category_id}>
                    Current category (retained)
                  </option>
                )}
              {categories.map((category) => (
                <option key={category.id} value={category.id}>
                  {category.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            Estimated minutes
            <input
              type="number"
              name="estimated_minutes"
              min={1}
              max={10080}
              defaultValue={task?.estimated_minutes ?? ""}
            />
          </label>
        </div>
        <label>
          Deadline
          <select
            aria-label="Deadline"
            value={deadline}
            onChange={(e) => setDeadline(e.target.value)}
          >
            <option value="none">No deadline</option>
            <option value="date">Date only</option>
            <option value="timed">Date and time</option>
          </select>
        </label>
        {deadline === "date" && (
          <label>
            Due date
            <input
              name="due_date"
              type="date"
              required
              defaultValue={task?.due_date ?? ""}
            />
            <small>
              Due by the end of this date in your account time zone.
            </small>
          </label>
        )}
        {deadline === "timed" && (
          <label>
            Due date and time
            <input
              name="due_at"
              type="datetime-local"
              required
              defaultValue={
                task?.due_at
                  ? new Date(
                      new Date(task.due_at).getTime() -
                        new Date(task.due_at).getTimezoneOffset() * 60000,
                    )
                      .toISOString()
                      .slice(0, 16)
                  : ""
              }
            />
            <small>
              Enter in this device’s time zone (
              {Intl.DateTimeFormat().resolvedOptions().timeZone}). It will
              display in your account time zone after saving.
            </small>
          </label>
        )}
        {error && (
          <p role="alert" className="notice error">
            {error.message}
          </p>
        )}
        <div className="dialog-actions">
          <button className="secondary" type="button" onClick={onCancel}>
            Cancel
          </button>
          <button className="primary" disabled={busy}>
            {busy ? "Saving…" : "Save task"}
          </button>
        </div>
      </fieldset>
    </form>
  );
}
