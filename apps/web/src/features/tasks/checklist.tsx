"use client";
import { useEffect, useState, useRef } from "react";
import { api, ApiError } from "@/services/api";
type Item = { id: string; title: string; completed: boolean; position: number };
export function Checklist({ taskId }: { taskId: string }) {
  const [items, setItems] = useState<Item[] | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [editing, setEditing] = useState<Item | null>(null);
  const [deleting, setDeleting] = useState<Item | null>(null);
  const guard = useRef(false);
  useEffect(() => {
    let active = true;
    api<Item[]>(`/tasks/${taskId}/checklist`)
      .then((rows) => {
        if (active) setItems(rows);
      })
      .catch((e: ApiError) => {
        if (active) setError(e.message);
      });
    return () => {
      active = false;
    };
  }, [taskId]);
  async function change(path: string, method: string, body?: object) {
    if (guard.current) return;
    guard.current = true;
    setBusy(true);
    setError("");
    try {
      await api(path, {
        method,
        ...(body ? { body: JSON.stringify(body) } : {}),
      });
      setItems(await api<Item[]>(`/tasks/${taskId}/checklist`));
      setEditing(null);
      setDeleting(null);
    } catch (e) {
      setError((e as ApiError).message);
    } finally {
      setBusy(false);
      guard.current = false;
    }
  }
  function move(index: number, delta: number) {
    if (!items) return;
    const ids = items.map((item) => item.id);
    [ids[index], ids[index + delta]] = [ids[index + delta], ids[index]];
    void change(`/tasks/${taskId}/checklist-order`, "PUT", { ids });
  }
  return (
    <section className="checklist" aria-label="Task checklist">
      <h3>
        Checklist{" "}
        {items && (
          <small>
            {items.filter((item) => item.completed).length} of {items.length}{" "}
            complete
          </small>
        )}
      </h3>
      <p className="muted">
        Checklist progress never automatically completes this task.
      </p>
      {error && <p role="alert">{error}</p>}
      {!items && !error && <p role="status">Loading checklist…</p>}
      <ul>
        {items?.map((item, index) => (
          <li key={item.id}>
            <label className="checkbox">
              <input
                type="checkbox"
                checked={item.completed}
                disabled={busy}
                onChange={() =>
                  void change(
                    `/tasks/${taskId}/checklist/${item.id}`,
                    "PATCH",
                    { completed: !item.completed },
                  )
                }
              />
              {item.title}
            </label>
            <div className="mini-actions">
              <button
                className="text-button"
                disabled={busy || index === 0}
                onClick={() => move(index, -1)}
                aria-label={`Move ${item.title} up`}
              >
                ↑
              </button>
              <button
                className="text-button"
                disabled={busy || index === items.length - 1}
                onClick={() => move(index, 1)}
                aria-label={`Move ${item.title} down`}
              >
                ↓
              </button>
              <button
                className="text-button"
                disabled={busy}
                onClick={() => setEditing(item)}
              >
                Edit<span className="sr-only"> {item.title}</span>
              </button>
              <button
                className="text-button danger-text"
                disabled={busy}
                onClick={() => setDeleting(item)}
              >
                Delete<span className="sr-only"> {item.title}</span>
              </button>
            </div>
          </li>
        ))}
      </ul>
      {items?.length === 0 && <p>No checklist items yet.</p>}
      {deleting && (
        <div className="notice error">
          <p>Delete checklist item “{deleting.title}”?</p>
          <button
            className="secondary"
            disabled={busy}
            onClick={() => setDeleting(null)}
          >
            Keep item
          </button>
          <button
            className="danger"
            disabled={busy}
            onClick={() =>
              void change(`/tasks/${taskId}/checklist/${deleting.id}`, "DELETE")
            }
          >
            Confirm item delete
          </button>
        </div>
      )}
      <form
        key={editing?.id ?? items?.length}
        onSubmit={(event) => {
          event.preventDefault();
          const data = new FormData(event.currentTarget);
          void change(
            `/tasks/${taskId}/checklist${editing ? `/${editing.id}` : ""}`,
            editing ? "PATCH" : "POST",
            { title: String(data.get("item_title")).trim() },
          );
        }}
      >
        <label>
          {editing ? "Edit checklist item" : "New checklist item"}
          <input
            name="item_title"
            disabled={busy}
            required
            maxLength={200}
            defaultValue={editing?.title ?? ""}
          />
        </label>
        <button
          className="secondary"
          disabled={busy || (!editing && items?.length === 100)}
        >
          {busy
            ? "Saving…"
            : editing
              ? "Save checklist item"
              : "Add checklist item"}
        </button>
        {editing && (
          <button
            type="button"
            className="text-button"
            onClick={() => setEditing(null)}
          >
            Cancel
          </button>
        )}
      </form>
    </section>
  );
}
