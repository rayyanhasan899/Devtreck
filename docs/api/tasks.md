# Task and category API — phase 4

Phase 5 update: daily complete/PATCH completed now work; daily reopen preserves credit. Task responses include nested streak metadata. Completed includes today's credited daily tasks, and Daily keeps completed-today habits visible. Daily-completion restrictions below describe the earlier phase and are superseded by the [current streak contract](streaks.md).

Use the updated API at http://127.0.0.1:8002/docs. Account registration/login and cookie/CSRF guide: accounts.md. All task/category operations require authenticated session cookie. Mutations additionally require an approved Origin and X-CSRF-Token; task route docs expose this header. Login returns token; GET /api/auth/csrf refreshes access to it. All results are no-store. There are no browser task screens yet.

## Routes

| Route | Behavior |
|---|---|
| POST /api/tasks | create task; 201 |
| GET /api/tasks | bounded TaskPage: items,total,limit,offset |
| GET /api/tasks/{id} | owned, nondeleted task |
| PATCH /api/tasks/{id} | partial update; omitted fields preserved |
| DELETE /api/tasks/{id}?confirm=true | archive task/history, remove from every public list; 204 |
| POST /api/tasks/{id}/complete | one-time task only; idempotent first completion |
| POST /api/tasks/{id}/reopen | one-time task pending, original completion fact preserved |
| GET /api/tasks/{id}/history | immutable server-timestamped one-time facts; bounded limit/offset |
| POST/GET /api/categories | create/list owned categories |
| GET/PATCH /api/categories/{id} | read/rename owned category |
| DELETE /api/categories/{id}?confirm=true | permanently delete category, keep tasks uncategorized |

Every unknown/foreign/deleted task ID returns privacy-preserving 404. UUID/enum/blank-title/invalid-query values return 422. Ownership also enforced on history, complete/reopen and category assignment. Cross-owner assignment cannot bypass composite FK at commit. No client owner/counter/timestamp fields accepted. Conflicts (duplicate category name, conflicting deadlines, daily completion) return 409 with safe error envelope. No reminders/tags alongside categories are silently accepted; those extra fields return validation errors.

## Task editor fields (typed source: presentation/task_schemas.py)

| Field | Create/default | Patch behavior |
|---|---|---|
| title | required trimmed 1–200 chars | nonblank; null rejected |
| description | optional/null, <=10000 chars | null clears |
| task_type | one-time (default), daily | changes reset current status pending and audit old/new type; no fabricated completions |
| priority | medium default; low/medium/high | null rejected |
| status | pending at creation; no create override | pending/in-progress/completed; completed goes through completion service |
| category_id | optional owned UUID | null uncategorizes |
| due_date | optional YYYY-MM-DD calendar date | null clears |
| due_at | optional timezone-aware ISO instant | null clears; naive instant rejected |
| estimated_minutes | optional integer 1–10080 | null clears |

Use either due_date OR due_at. Switching to timed deadline must explicitly clear old date, e.g. {"due_date":null,"due_at":"2030-01-01T12:00:00Z"}. Conflicting effective deadlines reject the entire update transaction. No date means no overdue state. Date-only task becomes overdue after its due calendar date in current user IANA zone, not at UTC midnight. Timed task becomes overdue immediately after due instant if unfinished. Due-date filter uses the timestamp's user-local date. Due sorting uses date-only next-local-midnight as deadline, timed instants as supplied, nulls always last and ID as stable tiebreaker. Server timestamps are UTC-aware; browsers must display in configured user zone.

## Lists

Parameters: view=all|today|upcoming|overdue|daily|completed; search (title/description literal substring, max200, escaped SQL wildcards); status/task_type/priority/category_id; due_date (user-local date); overdue boolean; sort=created_at|updated_at|title|priority|due_date; descending boolean default true; limit 1–100 default25; offset 0–10000 default0. Unknown query keys reject. Filters combine with AND; impossible combinations yield empty results. Sort order for priority is low<medium<high, title case-insensitive, dates chronological.

Default All excludes completed; explicit status=completed or completed view returns them. Today includes due today, overdue and daily tasks. Upcoming includes unfinished future-dated tasks. Daily includes daily-type unfinished tasks; daily completions are not enabled until phase 5. Completed includes one-time completed tasks. Date-only today is not overdue. Search/filter totals exclude foreign/archived rows and pagination has a stable tiebreaker.

## History and retention

One-time completion creates one unique fact per task for its lifetime. Reopen/recomplete cannot create another fact; editing due dates/type cannot rewrite its timestamp. Type changes append audit facts and daily activation time; enabling daily starts pending with no completion credit. POST complete/reopen and PATCH completed for daily return 409 until phase 5. No streak counters or daily completion assertions yet.

Task deletion archives until account deletion; no restore UI and no archived-list API. Retained content/history is private and excluded from active APIs. Account deletion physically removes tasks (including archived), category, completion and type-change data via cascades. Category names are unique per user, case-sensitive. Category deletion nulls only category_id, never user_id; a deferred composite owner FK validates ownership at commit while the simple SET NULL FK detaches tasks.

Generated Pydantic/OpenAPI schema is available at /openapi.json; do not expose ORM models as contracts or duplicate rules in UI. Account screens arrive in phase 6, task editor/list/dashboard in phase 7; no fake interactive pages introduced here.
