"use client";
import { useEffect, useRef, useState } from "react";
import { api, ApiError } from "@/services/api";
import { DailyPlan } from "./plan";
import { TaskEditor } from "./editor";
import { TaskDetail } from "./detail";
import {
  dateLabel,
  type Task,
  type TaskPage,
  type Category,
  type Summary,
  type View,
} from "./types";
const views: { value: View; label: string }[] = [
  { value: "today", label: "Today" },
  { value: "all", label: "All tasks" },
  { value: "upcoming", label: "Upcoming" },
  { value: "overdue", label: "Overdue" },
  { value: "daily", label: "Daily habits" },
  { value: "completed", label: "Completed" },
];
export function TaskBoard({
  initialView = "all",
  zone,
  name,
}: {
  initialView?: View;
  zone: string;
  name: string;
}) {
  const [view, setView] = useState<View>(initialView);
  const [filters, setFilters] = useState<Record<string, string>>({
    sort: "due_date",
    descending: "false",
  });
  const [offset, setOffset] = useState(0);
  const [search, setSearch] = useState("");
  const [tick, setTick] = useState(0);
  const [page, setPage] = useState<TaskPage | null>(null);
  const [categories, setCategories] = useState<Category[]>([]);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [busy, setBusy] = useState<string | null>(null);
  const guard = useRef(false);
  const [editing, setEditing] = useState<Task | "new" | null>(null);
  const [detail, setDetail] = useState<Task | null>(null);
  const [deleting, setDeleting] = useState<Task | null>(null);
  const [categoryEdit, setCategoryEdit] = useState<Category | null>(null);
  const [categoryDelete, setCategoryDelete] = useState<Category | null>(null);
  const [categoryBusy, setCategoryBusy] = useState(false);
  const [categoryError, setCategoryError] = useState("");
  const [moreCategories, setMoreCategories] = useState(true);
  const editor = useRef<HTMLDialogElement>(null);
  const details = useRef<HTMLDialogElement>(null);
  const confirmation = useRef<HTMLDialogElement>(null);
  const manager = useRef<HTMLDialogElement>(null);
  function reload(message = "") {
    setNotice(message);
    setError("");
    setPage(null);
    setTick((value) => value + 1);
  }
  useEffect(() => {
    let active = true;
    const query = new URLSearchParams({
      view,
      limit: "10",
      offset: String(offset),
      ...Object.fromEntries(
        Object.entries(filters).filter(([, value]) => value !== ""),
      ),
    });
    Promise.all([
      api<TaskPage>(`/tasks?${query}`),
      api<Category[]>("/categories?limit=100"),
      api<Summary>("/dashboard"),
    ])
      .then(([result, cats, total]) => {
        if (active) {
          setPage(result);
          setCategories(cats);
          setMoreCategories(cats.length === 100);
          setSummary(total);
        }
      })
      .catch((e: ApiError) => {
        if (active) setError(e.message);
      });
    return () => {
      active = false;
    };
  }, [view, filters, offset, tick]);
  useEffect(() => {
    const refresh = () => {
      if (
        !editor.current?.open &&
        !details.current?.open &&
        !manager.current?.open &&
        !confirmation.current?.open
      ) {
        setPage(null);
        setTick((value) => value + 1);
      }
    };
    window.addEventListener("focus", refresh);
    const timer = setInterval(refresh, 60000);
    return () => {
      window.removeEventListener("focus", refresh);
      clearInterval(timer);
    };
  }, []);
  function filter(key: string, value: string) {
    setPage(null);
    setOffset(0);
    setFilters((current) => ({ ...current, [key]: value }));
  }
  function openEditor(task: Task | "new") {
    setEditing(task);
    editor.current?.showModal();
  }
  async function change(task: Task, action: "complete" | "reopen" | "delete") {
    if (guard.current) return;
    guard.current = true;
    setBusy(task.id);
    setError("");
    try {
      await api(
        `/tasks/${task.id}${action === "delete" ? "?confirm=true" : `/${action}`}`,
        { method: action === "delete" ? "DELETE" : "POST" },
      );
      confirmation.current?.close();
      reload(
        action === "delete"
          ? "Task archived."
          : action === "reopen"
            ? "Task reopened. Completion history is preserved."
            : "Completion recorded.",
      );
    } catch (e) {
      setError((e as ApiError).message);
    } finally {
      guard.current = false;
      setBusy(null);
    }
  }
  async function saveCategory(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (categoryBusy) return;
    setCategoryBusy(true);
    setCategoryError("");
    const data = new FormData(event.currentTarget);
    try {
      await api(
        categoryEdit ? `/categories/${categoryEdit.id}` : "/categories",
        {
          method: categoryEdit ? "PATCH" : "POST",
          body: JSON.stringify({
            name: String(data.get("category_name")).trim(),
          }),
        },
      );
      setCategoryEdit(null);
      reload("Category saved.");
    } catch (e) {
      setCategoryError((e as ApiError).message);
    } finally {
      setCategoryBusy(false);
    }
  }
  async function removeCategory(category: Category) {
    if (categoryBusy) return;
    setCategoryBusy(true);
    setCategoryError("");
    try {
      await api(`/categories/${category.id}?confirm=true`, {
        method: "DELETE",
      });
      setCategoryDelete(null);
      if (categoryEdit?.id === category.id) setCategoryEdit(null);
      if (filters.category_id === category.id) {
        setFilters((current) => ({ ...current, category_id: "" }));
        setOffset(0);
      }
      reload("Category deleted. Its tasks are now uncategorized.");
    } catch (e) {
      setCategoryError((e as ApiError).message);
    } finally {
      setCategoryBusy(false);
    }
  }
  return (
    <main id="main" className="workspace-main task-workspace">
      <div className="task-heading">
        <div>
          <p className="eyebrow">MAKE SPACE FOR WHAT MATTERS</p>
          <h1>
            {view === "today"
              ? `Your day, ${name.split(" ")[0]}.`
              : views.find((item) => item.value === view)?.label}
          </h1>
          <p className="muted">
            {view === "daily"
              ? "One small step each day. Your streaks follow your account time zone."
              : "Capture it. Give it a place. Take the next step."}{" "}
            <span>{zone}</span>
          </p>
        </div>
        <button className="primary" onClick={() => openEditor("new")}>
          Add task
        </button>
      </div>
      {summary && (
        <section className="summary-grid" aria-label="Your task summary">
          <div>
            <span>To do today</span>
            <strong>{summary.today_actionable}</strong>
          </div>
          <div>
            <span>Completions today</span>
            <strong>{summary.completions_today}</strong>
          </div>
          <div>
            <span>Outstanding</span>
            <strong>{summary.outstanding}</strong>
          </div>
          <div>
            <span>Daily habits done</span>
            <strong>
              {summary.daily_done}
              <small>of {summary.daily_total}</small>
            </strong>
          </div>
        </section>
      )}
      {view === "today" && (
        <details className="settings-card">
          <summary>Plan your day</summary>
          <DailyPlan key={tick} />
        </details>
      )}
      <nav className="task-views" aria-label="Task views">
        {views.map((item) => (
          <button
            key={item.value}
            aria-pressed={view === item.value}
            onClick={() => {
              setView(item.value);
              setSearch("");
              setPage(null);
              setOffset(0);
              setFilters({ sort: "due_date", descending: "false" });
            }}
          >
            {item.label}
          </button>
        ))}
      </nav>
      <section className="task-list-panel" aria-label="Task list">
        <form
          className="task-search"
          onSubmit={(event) => {
            event.preventDefault();
            filter(
              "search",
              String(new FormData(event.currentTarget).get("search") || ""),
            );
          }}
        >
          <label>
            Search tasks
            <input
              name="search"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              type="search"
              maxLength={200}
              placeholder="Title or description"
            />
          </label>
          <button className="secondary">Search</button>
          <button
            type="button"
            className="text-button"
            onClick={() => {
              setCategoryError("");
              manager.current?.showModal();
            }}
          >
            Manage categories
          </button>
        </form>
        <details className="filters-disclosure">
          <summary>Filters and sorting</summary>
          <div className="task-filters">
            <label>
              Status
              <select
                aria-label="Filter status"
                value={filters.status ?? ""}
                onChange={(e) => filter("status", e.target.value)}
              >
                <option value="">Any status</option>
                <option value="pending">Pending</option>
                <option value="in-progress">In progress</option>
                <option value="completed">Completed</option>
              </select>
            </label>
            <label>
              Priority
              <select
                aria-label="Filter priority"
                value={filters.priority ?? ""}
                onChange={(e) => filter("priority", e.target.value)}
              >
                <option value="">Any priority</option>
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </label>
            <label>
              Type
              <select
                aria-label="Filter type"
                value={filters.task_type ?? ""}
                onChange={(e) => filter("task_type", e.target.value)}
              >
                <option value="">Any type</option>
                <option value="one-time">One-time</option>
                <option value="daily">Daily</option>
              </select>
            </label>
            <label>
              Category
              <select
                aria-label="Filter category"
                value={filters.category_id ?? ""}
                onChange={(e) => filter("category_id", e.target.value)}
              >
                <option value="">All categories</option>
                {categories.map((category) => (
                  <option key={category.id} value={category.id}>
                    {category.name}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Due date
              <input
                aria-label="Filter due date"
                type="date"
                value={filters.due_date ?? ""}
                onChange={(e) => filter("due_date", e.target.value)}
              />
            </label>
            <label>
              Overdue
              <select
                aria-label="Filter overdue"
                value={filters.overdue ?? ""}
                onChange={(e) => filter("overdue", e.target.value)}
              >
                <option value="">Any deadline</option>
                <option value="true">Overdue only</option>
                <option value="false">Not overdue</option>
              </select>
            </label>
            <label>
              Sort by
              <select
                value={filters.sort}
                onChange={(e) => filter("sort", e.target.value)}
              >
                <option value="due_date">Deadline</option>
                <option value="priority">Priority</option>
                <option value="created_at">Created</option>
                <option value="updated_at">Updated</option>
                <option value="title">Title</option>
              </select>
            </label>
            <label>
              Order
              <select
                value={filters.descending}
                onChange={(e) => filter("descending", e.target.value)}
              >
                <option value="false">Ascending</option>
                <option value="true">Descending</option>
              </select>
            </label>
          </div>
        </details>
        {notice && (
          <p role="status" className="notice success">
            {notice}
          </p>
        )}
        {error && (
          <div className="notice error">
            <p role="alert">{error}</p>
            <button className="secondary" onClick={() => reload()}>
              Try again
            </button>
          </div>
        )}
        {!page && !error && (
          <p className="task-loading" role="status">
            Loading your tasks…
          </p>
        )}
        {page && (
          <>
            <p className="result-count">
              {page.total} {page.total === 1 ? "task" : "tasks"}{" "}
              {filters.search ? `matching “${filters.search}”` : "in this view"}
            </p>
            {page.items.length === 0 && (
              <div className="task-empty">
                <h2>
                  {view === "today"
                    ? "A little breathing room."
                    : "No tasks here yet."}
                </h2>
                <p>
                  {view === "today"
                    ? "You have no outstanding tasks in Today. Check All tasks or add something meaningful."
                    : "Try another view or filter, or capture your next task."}
                </p>
                <button className="secondary" onClick={() => openEditor("new")}>
                  Create a task
                </button>
              </div>
            )}
            <div className="task-rows">
              {page.items.map((task) => {
                const done =
                  task.task_type === "daily"
                    ? task.streak?.today_completed
                    : task.status === "completed";
                return (
                  <article
                    className="task-row"
                    key={task.id}
                    aria-label={task.title}
                  >
                    <div className="task-row-main">
                      <button
                        className="task-title"
                        onClick={() => {
                          setDetail(task);
                          details.current?.showModal();
                        }}
                      >
                        {task.title}
                      </button>
                      <div className="task-meta">
                        <span className={`priority priority-${task.priority}`}>
                          {task.priority} priority
                        </span>
                        <span>
                          {task.task_type === "daily"
                            ? done
                              ? "Completed today"
                              : "Daily · pending today"
                            : task.status.replace("-", " ")}
                        </span>
                        <span>{dateLabel(task, zone)}</span>
                        {task.category_id && (
                          <span>
                            {categories.find(
                              (category) => category.id === task.category_id,
                            )?.name ?? "Category"}
                          </span>
                        )}
                        {task.estimated_minutes && (
                          <span>~{task.estimated_minutes} min</span>
                        )}
                      </div>
                      {task.checklist_total > 0 && (
                        <p className="row-streak">
                          Checklist: {task.checklist_completed} of{" "}
                          {task.checklist_total} complete
                        </p>
                      )}
                      {task.streak && (
                        <p className="row-streak">
                          Current streak {task.streak.current_streak} · Best{" "}
                          {task.streak.best_streak}
                        </p>
                      )}
                    </div>
                    <div className="task-actions">
                      <button
                        className={done ? "secondary" : "primary"}
                        disabled={
                          !!busy || (task.task_type === "daily" && !!done)
                        }
                        onClick={() =>
                          void change(task, done ? "reopen" : "complete")
                        }
                      >
                        {busy === task.id
                          ? "Saving…"
                          : done
                            ? task.task_type === "daily"
                              ? "Done today"
                              : "Reopen"
                            : "Complete"}
                      </button>
                      <button
                        className="secondary"
                        onClick={() => openEditor(task)}
                        disabled={!!busy}
                      >
                        Edit
                      </button>
                      <button
                        className="text-button danger-text"
                        onClick={() => {
                          setError("");
                          setDeleting(task);
                          confirmation.current?.showModal();
                        }}
                        disabled={!!busy}
                      >
                        Delete
                      </button>
                    </div>
                  </article>
                );
              })}
            </div>
            <div className="pagination">
              <button
                className="secondary"
                disabled={offset === 0}
                onClick={() => {
                  setPage(null);
                  setOffset(offset - 10);
                }}
              >
                Previous
              </button>
              <span>Page {Math.floor(offset / 10) + 1}</span>
              <button
                className="secondary"
                disabled={offset + 10 >= page.total}
                onClick={() => {
                  setPage(null);
                  setOffset(offset + 10);
                }}
              >
                Next
              </button>
            </div>
          </>
        )}
      </section>
      <dialog
        ref={editor}
        aria-labelledby="editor-title"
        onClose={() => setEditing(null)}
      >
        <h2 id="editor-title">
          {editing === "new" ? "Add a task" : "Edit task"}
        </h2>
        {editing && (
          <TaskEditor
            key={editing === "new" ? "new" : editing.id}
            task={editing === "new" ? undefined : editing}
            categories={categories}
            onCancel={() => editor.current?.close()}
            onSaved={() => {
              editor.current?.close();
              reload("Task saved.");
            }}
          />
        )}
      </dialog>
      <dialog
        ref={details}
        aria-labelledby="detail-title"
        onClose={() => {
          setDetail(null);
          reload();
        }}
      >
        <div className="dialog-heading">
          <h2 id="detail-title">{detail?.title}</h2>
          <button
            className="secondary"
            onClick={() => details.current?.close()}
          >
            Close
          </button>
        </div>
        {detail && (
          <TaskDetail
            key={detail.id}
            task={detail}
            zone={zone}
            onEdit={() => {
              details.current?.close();
              openEditor(detail);
            }}
          />
        )}
      </dialog>
      <dialog
        ref={confirmation}
        aria-labelledby="delete-task-title"
        onClose={() => setDeleting(null)}
      >
        <h2 id="delete-task-title">Delete this task?</h2>
        <p>
          “{deleting?.title}” will leave your task lists. Its private history is
          retained until account deletion.
        </p>
        {error && <p role="alert">{error}</p>}
        <div className="dialog-actions">
          <button
            className="secondary"
            disabled={!!busy}
            onClick={() => confirmation.current?.close()}
          >
            Keep task
          </button>
          <button
            className="danger"
            disabled={!!busy}
            onClick={() => deleting && void change(deleting, "delete")}
          >
            {busy ? "Deleting…" : "Confirm delete"}
          </button>
        </div>
      </dialog>
      <dialog ref={manager} aria-labelledby="categories-title">
        <div className="dialog-heading">
          <h2 id="categories-title">Manage categories</h2>
          <button
            className="secondary"
            onClick={() => manager.current?.close()}
          >
            Close
          </button>
        </div>
        <form onSubmit={saveCategory}>
          <label>
            Category name
            <input
              key={categoryEdit?.id ?? tick}
              name="category_name"
              defaultValue={categoryEdit?.name ?? ""}
              required
              maxLength={80}
            />
          </label>
          <button className="primary" disabled={categoryBusy}>
            {categoryBusy
              ? "Saving…"
              : categoryEdit
                ? "Rename category"
                : "Add category"}
          </button>
          {categoryEdit && (
            <button
              type="button"
              className="secondary"
              onClick={() => setCategoryEdit(null)}
            >
              Cancel rename
            </button>
          )}
        </form>
        {categoryError && <p role="alert">{categoryError}</p>}
        <ul className="category-list">
          {categories.map((category) => (
            <li key={category.id}>
              <span>{category.name}</span>
              <button
                className="text-button"
                disabled={categoryBusy}
                onClick={() => setCategoryEdit(category)}
              >
                Rename<span className="sr-only"> {category.name}</span>
              </button>
              <button
                className="text-button danger-text"
                disabled={categoryBusy}
                onClick={() => setCategoryDelete(category)}
              >
                Delete<span className="sr-only"> {category.name}</span>
              </button>
            </li>
          ))}
        </ul>
        {categories.length === 0 && (
          <p>No categories yet. Create one to organize your tasks.</p>
        )}
        {moreCategories && (
          <button
            className="secondary"
            onClick={async () => {
              try {
                const more = await api<Category[]>(
                  `/categories?limit=100&offset=${categories.length}`,
                );
                setCategories((current) => [...current, ...more]);
                setMoreCategories(more.length === 100);
              } catch (e) {
                setCategoryError((e as ApiError).message);
              }
            }}
          >
            Load more categories
          </button>
        )}
        {categoryDelete && (
          <section
            className="notice error"
            aria-label="Confirm category deletion"
          >
            <p>
              Delete “{categoryDelete.name}”? Its tasks will become
              uncategorized.
            </p>
            <button
              className="secondary"
              onClick={() => setCategoryDelete(null)}
            >
              Keep category
            </button>
            <button
              className="danger"
              disabled={categoryBusy}
              onClick={() => void removeCategory(categoryDelete)}
            >
              Confirm category delete
            </button>
          </section>
        )}
      </dialog>
    </main>
  );
}
