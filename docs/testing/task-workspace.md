# Task workspace verification and usage

Open http://127.0.0.1:3000 and sign in. Today shows due-today, overdue and unfinished daily tasks. All tasks includes active tasks and daily habits; Completed includes completed one-time tasks and today's daily credit. Daily habits retains done-today entries and their current/best streak.

Add task opens an editor for title, description, type, priority, optional category/duration and calendar-date or timed deadline. Timed input is explicitly in device zone; saved dates display in account zone. Undated one-time tasks belong in All tasks, not Today. Click title for description/streak/history and Edit for changes. Complete/reopen use server operations; daily completion credit cannot be undone. Delete requires confirmation and archives task/history until account deletion. Manage categories supports create/rename and confirmed delete without deleting tasks.

Search title/description; expand Filters and sorting for status, priority, type, category, due date, overdue and ordering. Filters combine, so incompatible choices may return empty results. View changes clear filters/search and reset pagination. Task pages contain 10 rows; history pages 25; category manager loads more in 100-row batches. Page view/filter choices are local UI state and reset on route reload; persistent planning/order is later scope.

Dashboard cards are server totals, not totals estimated from the current page. Completions today counts source records, so reopening a task preserves its recorded completion count. Archived task records excluded from these displayed totals. /api/dashboard inherits authentication and owner isolation.

From repository root, use the established disposable browser runner:

```powershell
apps/api/.venv/Scripts/python apps/api/scripts/browser_checks.py
```

Focused task regression:

```powershell
apps/api/.venv/Scripts/python apps/api/scripts/browser_checks.py tasks.spec.ts
```

Full browser suite includes three account journeys and two task journeys. Tasks cover register/create/edit/category/description/priority/duration/deadline, one-time and daily complete, streak/history, search/filter, category rename/delete, reopen/archive/cancel, dashboard, logout, 360/768/1440 widths, axe checks, honest failed-save behavior, 10-row pagination and two-account API/UI privacy. Backend tests separately verify all filters/sorts/views, timezone boundaries, constraints and concurrency.

Screenshots/traces use disposable data and remain ignored in apps/web/test-results. Runner owns/cleans random database and temporary services; normal local accounts are untouched. Production smoke checks and build are separate from development-server browser journeys. No Safari/Firefox/hosted CI result is implied by local Chromium success.

## Phase 9 verification

The suite now includes Progress in addition to account/task/productivity journeys. `apps/api/.venv/Scripts/python apps/api/scripts/browser_checks.py progress.spec.ts` runs only the new journey; omit the filename for all seven. API `tests/test_progress.py` verifies exact 50%/12.5% denominator fixtures, empty/unknown coverage, idle daily dates and type conversion, local-midnight/DST focus splitting, immutable reward policy, concurrency/rollback/toggle/backfill/caps/achievements and deletion ownership. Progress browser checks empty/populated state, reload and network recovery, preserved XP after archive, accessible table/landmarks, axe and 360/768/1440 widths. Ignored screenshots are progress-desktop.png and progress-mobile.png.

## Phase 10 integrated release check

Final regular suite remains seven journeys; production Docker HTTPS is a separate additional journey under apps/web/release-tests with playwright.release.config.ts. Follow docs/testing/release-readiness.md and deployment runbook for API security/query checks, synthetic all-table backup/restore, safe logging, TLS/role/header/size checks and sequential API outage/recovery. Never run outage checks concurrently with a browser journey or against live external resources. Final production screenshots copied into ignored root .release-results before the normal suite cleans its test-results directory.
