# Phase 07 report — Core task and dashboard experience

Date: 2026-11-07, Asia/Karachi. Status: **PASS WITH KNOWN LIMITATIONS**.

## Objective and implemented functionality

Protected Today, All tasks and Daily habits routes share all six views: All, Today, Upcoming, Overdue, Daily and Completed. Task editor/detail support title, description, task type, status, priority, category, estimated duration, calendar-date or timed deadline. Search/filter/sort and ten-row pagination use server contracts. Title opens description/streak/history, with bounded history pages. One-time completion/reopen and daily completion use backend workflows, and current/best/today streak metadata stays server-authoritative.

Daily view retains completed-today habits and disables repeat completion; Today excludes them. All retains daily habits for visibility. Completed includes one-time completed tasks and today's qualified habits. Completion/history persists after reopen/type changes according to phase 5 rules. Task deletion requires confirmation and discloses private archive retention. Category manager supports create/rename and confirmed delete that leaves tasks uncategorized; current category filter clears on deletion.

New /api/dashboard reports actual owner-scoped actionable Today, outstanding, recorded completions today and daily credited/total counts. Counts exclude archived tasks. Reopen preserves the first-completion record and its count; these are record totals, not percentages or estimates. No new schema/index justified; no migration added.

Writes wait for confirmation before reloading lists and totals. Failed mutation leaves saved task state unchanged and shows an error. Empty/loading/success/error/retry states, guarded submissions, native modal focus/cancel, expandable filters, semantic labels and keyboard controls are present. Refresh on focus/minute avoids interrupting dialogs. Account/settings functionality remains usable.

## Requirements, files and decisions

TSK-01–32: browser task CRUD/editor, fields, views, validations, owner scope, search/sort/filter, completion/reopen/history and delete confirmation; optional reminders remain deferred. STR-01–11: browser occurrence state/current/best/history consume verified server engine; no client counters trusted. UI-01–13 and PLN-01: Today summaries/work list, scan-friendly task metadata, states, responsive controls, keyboard/focus/contrast, consistent zone display and existing settings. Requirements 16.2–16.3 covered through browser/API evidence; clock/DST/concurrency rules remain backend-tested.

Added features/tasks types, board, editor and detail components; protected tasks/daily routes. Updated Today page, shell navigation, API error messages and task CSS. Extended API persistence/service/schema/route with owner-filtered dashboard aggregates, added dashboard integration test and task browser spec; runner now forwards optional test filename arguments. Added ADR-0007 and task usage/testing guide; updated README/assumptions/report. No user files deleted, no dependency changes, no schema migration.

ADR-0007 explains server totals, confirmed writes, bounded data, dialogs and deadline interpretation. A-36–40 record shared routes/views, ten-row pages, confirmation before refresh, completion-fact counts, device-zone timed entry/account-zone display and archive/category notices. Optional reminders, smart priorities/manual planning, focus, checklists, rewards and insights remain later scope.

## Verification and evidence

Retained existing Node 24/Next.js 16.4.5/React 19.3.0/Python 3.14.7/SQLAlchemy 2.1.8/Alembic 1.20.1/PostgreSQL 18.6 and locked packages. Installed Next.js server/client documentation consulted. No package upgrades or installation needed. Frontend source formatted with Prettier.

- Backend full pytest: **53 passed**, including new dashboard totals/privacy test and all prior account/task/streak/migration/security regressions. New test verifies initial actionable/outstanding counts, one-time/daily completion, reopen record preservation, archive exclusion, anonymous rejection and two-user separation.
- Backend Ruff lint/format passed (40 files); mypy passed (34 application modules); pip check passed.
- Frontend lint, strict type checks and production build passed. npm audit reported zero vulnerabilities. New dynamic /app/tasks and /app/daily routes generated correctly.
- Three account browser journeys passed during full suite runs with the new navigation/workspace.
- Two task browser journeys passed after final task adjustments (focused runner: 2 passed, 21.5 seconds). Combined verified coverage is five journeys; the final focused rerun did not redundantly rerun unchanged account flows.
- Task journey: register/login, category create/rename/delete, one-time and daily create, description/title/category/priority/duration edit, complete daily, current streak one and preserved history, search/priority filter, one-time complete/history/reopen, Today, delete cancel/confirm and logout.
- Second journey: failed completion request preserves visible saved task, API-driven synthetic setup for 12 records, ten-row Next/Previous pagination, independent second browser account sees no first-user records and receives 404 for substituted task ID.
- Axe task-screen scan passed with zero violations. Overflow checks passed at 360/768/1440 widths; desktop/mobile screenshots inspected. Screenshot review motivated expandable filters so mobile users can keep them closed. Earlier phase 6 keyboard/skip/dialog tests still pass; task controls use native semantic controls.
- Browser runner uses guarded random disposable PostgreSQL databases and temporary 8010/3100 services, then removes only its resources. No local user accounts modified by tests.
- Refreshed production web on 3000 and API on 8002: login HTTP 200, readiness 200, dashboard through web proxy returns 401 without authentication. Full browser journeys use isolated development servers; production build/HTTP smoke verified separately.
- git diff --check passed before commits. No new migrations; previous schema unchanged and migration regressions passed in disposable databases.

## Failures resolved

Initial browser checks caught ambiguous category text matches and exact select-label mismatch; narrowed test selection and provided explicit editor select labels. Search-box role/manual second-context base URL were corrected in tests. Failed-save assertion initially matched an alert inside a hidden dialog; scoped to the visible task-list region and cleared old errors when opening deletion. Search draft now clears visibly with view changes. Category deletion clears a selected filter and any rename state for that category. Final task journeys pass with category management and collapsed-filter controls exercised. No unresolved application/test failure.

## Security, integrity and known limits

Every private request uses existing session/CSRF/origin safeguards. Dashboard filtering and calculations remain in persistence/service; no query/body user ID trusted. React text rendering handles descriptions without raw HTML. No optimistic completion/streak counters, browser credential storage or data-reset operation introduced. Task status completion is always server-side. Ignored screenshots/logs contain disposable test records only; no real credentials committed or printed.

Known limits: local Windows Chromium verified; hosted CI/Linux and broader browser/assistive-technology matrix not claimed. Views/filter choices are transient local state and reset on route reload. Timed entry explicitly uses device zone; ambiguous seasonal times follow browser Date conversion, while displayed time uses account zone. Large-history performance still requires measured work. Histories stay in separate one-time/daily sections and page together by 25. Category manager loads more in bounded 100-row batches; selected existing category is retained even if outside the initial batch. Recovery/freeze/reminders and phase 8 productivity features remain out of scope.

## Git and handover

Branch codex/phase-07. 1b1aa8c implements task workspace/dashboard; 4cbb5b7 adds browser/dashboard tests; final documentation commit records evidence. Main/private origin unchanged; no push, PR, merge, reset or history rewrite. No manual setup action required.

**Usable now at http://127.0.0.1:3000:** account/settings, Today dashboard, task CRUD/search/filter/sort, all six views, categories, one-time complete/reopen, daily completion/streak/history and confirmed deletion. API docs remain at 8002. **Next:** planning priorities, focus, checklists and later rewards/insights; phase 8 has not started.
