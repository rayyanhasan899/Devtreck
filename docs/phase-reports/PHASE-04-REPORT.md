# Phase 04 report — Task and category APIs

2026-11-07, Asia/Karachi. Status: **PASS WITH KNOWN LIMITATIONS**.

## Objective and implemented functionality

Owner-scoped task CRUD, partial updates, statuses/priorities, date-only or timed deadlines, estimated duration, categories, escaped title/description search, allowlisted sorting, filters, bounded result pages and All/Today/Upcoming/Overdue/Daily/Completed views. One-time tasks support idempotent completion, reopen and preserved server-generated completion history. Daily tasks can be created/edited, but complete/reopen and PATCH completed reject with 409 until phase 5.

Custom categories support create/list/read/rename/delete. Category deletion keeps tasks and clears category_id. Composite owner FK prevents cross-account assignment even through direct persistence; deferred validation allows SET NULL actions to finish before ownership is checked at commit. Task deletion requires confirm=true and archives the task/content/history until account deletion, hidden from every public task endpoint. Account deletion cascades categories/tasks/completion/type-change records, including archived tasks.

## Requirements addressed

TSK-01–06 task creation and validation: TaskInput, service/create and owner-derived persistence; daily eligibility remains phase 5 behavior. TSK-07/12 are frontend interaction requirements deferred to phase 7; APIs provide success/error and empty bounded lists now. TSK-08–11 reads and history: owner-filtered queries, private detail/history. TSK-13–19 edits: partial/null semantics, updated timestamp, type audit and daily activation, immutable past facts; optional reminders remain deferred. TSK-20–22 one-time completion: trusted timestamp and active-list exclusion; daily completion explicitly remains phase 5. TSK-24–26 reopen/delete: retained first completion, confirm/archive and ownership. TSK-28–32 search/filter/sort/views: owner scoping, pagination and SQL-safe parameterized queries. SEC-01–03/06–07 and requirements 5–6/12/15: authentication/CSRF/origin reuse, validation, composite ownership, bounded contracts and safe errors. No claim that deferred UI/daily features are complete.

## Files, architecture and decisions

Added domain/tasks.py (framework-free query value), persistence/tasks.py, services/tasks.py, presentation/task_schemas.py and tasks.py; extended composition, models and safe field-name validation details. Added migration eb92ac3655cd for categories/tasks/completions/type-change audit, indexes/checks/owner constraints. Added test_tasks.py; no files deleted and no dependency upgrades/installations required. Updated README/Assumptions and added task API/editor field specification and ADR-0004.

Routes validate/serialize; application service owns lifecycle and transaction; persistence owns all queries and owner filtering. Explicit Pydantic contracts remain distinct from ORM. Current authenticated user row lock and task row lock serialize same-user mutations; DB uniqueness protects first completion. Task view totals exclude archived/foreign records. No frontend feature screens or nonfunctional buttons added.

ADR-0004 records archive retention, first-ever one-time completion, category deletion/ownership, deadline semantics and type audits. A-03/04/06 implemented defaults; A-10 foundation only; A-25–27 document field limits, case-sensitive category names, list defaults and delete confirmation. These follow the authorized phase plan; historical daily streak policies remain phase 5.

## Verification and tools

Used existing Python 3.14.7, SQLAlchemy 2.1.8, Alembic 1.20.1, psycopg 3.3.8, PostgreSQL 18.6, Node 24 and locked dependencies. SQLAlchemy constraint documentation checked against installed 2.1 behavior. Commands from apps/api:

- python -m ruff check .: passed.
- python -m ruff format --check .: 36 files passed.
- python -m mypy app: 32 source files passed.
- python -m pytest: **31 tests passed** (8 task tests plus 23 previous security/persistence tests); final targeted task rerun also passed 8/8.
- python -m pip check: no broken requirements.
- Disposable database migration upgrade/base/head round-trip and alembic check: passed as part of persistence suite.
- Local development python -m alembic upgrade head/current/check: eb92ac3655cd head, no new operations/schema drift.

Task tests prove full CRUD, trimmed titles, preserved omitted fields/null clearing, status changes, duplicate complete/reopen history, archive visibility, category CRUD/SET NULL, direct-DB foreign owner rejection, ID substitution for every task operation/history, owner-only list/category access, invalid enums/IDs/dates/naive timestamps/limits/sorts, CSRF rejection, every view and sort, priority/type/category/status/due/overdue/search filters, literal wildcard handling, pagination/empty results, timezone-aware date-only versus timed overdue, partial deadline replacement, type audit/history preservation, daily completion rejection, account cascade and concurrent one-time completion yielding one fact. Impossible upcoming/completed combination yields empty result.

From apps/web: npm run lint, npm run typecheck and npm run build passed without frontend changes. Live API on port 8002: /ready HTTP 200; /openapi.json exposes task/category collections. Development API restarted from phase 3 on same port for inspection; old 8000/8001 APIs may still run older code.

## Failures resolved

Initial integration suite had one failure: category delete returned conflict because immediate composite owner FK checked before SET NULL detached tasks. Deferred composite validation resolved it; direct foreign-category commits still fail. Reran category/lifecycle suite successfully, then full suite. Ruff formatting/import fixes and a final active-view filter correction were verified. No unresolved test failure.

## Data integrity, security and limitations

No client user ID/counter/timestamp is trusted. Unknown/foreign/archived IDs yield 404; query values are validated and bound. Search escapes SQL wildcard characters; sorts are allowlisted and lists bounded. All mutations require approved Origin and session-bound CSRF. No credentials/log contents printed or committed. Tests created/dropped only guarded random disposable databases; local development migration added tables without resetting existing data. No production operation or destructive data migration.

One-time immutable facts have no update/delete API; account cascade removes them intentionally. Reopen/recomplete preserves original timestamp. Audit records preserve type transitions; daily activation starts pending without invented credit. Calendar deadlines become overdue after chosen local day; timed deadlines compare server instant. Changing timezone changes current views, not stored records.

Known limits: daily completion/streaks phase 5; auth/task browser screens phases 6/7; reminders and extra tags deferred; hosted CI/Linux execution not run here. Task archive has no restore/list UI; retained until account deletion. No XP rewards yet; future rewards must reference first completion fact, not status toggles. Initial migrations/indexes serve expected access patterns; full performance/load/a11y/browser checks belong to later integration phases. No deployment/push/PR/merge claimed.

## Git and handover

Branch codex/phase-04. f48e59a implements API/schema; 9073ac6 adds task tests; final documentation commit records evidence. Main and private origin preserved, no history rewrites; no push or PR. No manual setup action required.

**What you can use now:** through http://127.0.0.1:8002/docs or an API client, register/login, manage profile/password, create/edit/list/search/filter/sort/archive tasks, complete/reopen one-time tasks, view completion history and manage categories. Daily tasks are creatable but not completable yet. The website remains a welcome page until the scheduled UI phases. Read docs/api/tasks.md for fields, CSRF header and delete confirmations. Phase 4 exit criteria met; await phase 5 prompt.
