# Devtreck

Current phase 10: local release readiness is verified with an isolated Docker HTTPS stack, restricted database role, explicit migrations, security/query checks and a synthetic backup/restore drill. All account/task/habit/planning/focus/checklist/reward features remain usable at [local Devtreck](http://127.0.0.1:3000). See the [release runbook](docs/deployment/RUNBOOK.md), [personal $0 hosting plan](docs/deployment/FREE-HOSTING.md), [audit](docs/testing/release-readiness.md) and [phase report](docs/phase-reports/PHASE-10-REPORT.md). External deployment is **BLOCKED** pending usable Vercel/Render account access, billing safeguards and production migration approval; nothing is live externally. The latest user decision is personal use only for now.

Current phase 9: [Progress](http://127.0.0.1:3000/app/progress) adds XP, levels, milestone badges, today/seven-date completion rates, focus totals and daily/category insights. Accounts, tasks, habits, daily planning, focus and checklists remain available. Historical rates with unknown denominators explicitly show unavailable. See [Progress rules](docs/api/progress.md). All phase descriptions below record earlier delivery milestones.

Current phase 8: Daily plan lets you choose three priorities and reorder Today's work with workload estimates. Focus supports configurable focus/break sessions, pause/resume/stop, refresh recovery and history/totals. Task details now contain checklists with progress and keyboard ordering. Existing account/task/habit features remain. See [productivity guide](docs/api/productivity.md). XP/rewards/insights remain phase 9.

Current phase 7: [open Devtreck](http://127.0.0.1:3000) to use Today, All tasks, Daily habits and Completed views; create/edit/search/filter/sort tasks, manage categories, complete/reopen one-time tasks, complete daily habits and inspect streak/history. Task and category deletion require confirmation. All account/settings features remain available. Focus, planning priorities, checklists and rewards are later phases. See [task workspace guide](docs/testing/task-workspace.md).

Current phase 6: open http://127.0.0.1:3000 to create an account, sign in, use your protected overview and edit Settings (profile, timezone, theme, email, password and confirmed deletion). Sign out is available on desktop/mobile. Task/habit APIs are available, while their browser screens arrive in phase 7.

Web server-only API_ORIGIN defaults to http://127.0.0.1:8002. Set it before build and at runtime if changing API address; never use a public environment variable for secrets. Keep the API running, then build/start web with `npm run build` and `npm start` from apps/web. Browser /api requests use the same origin as the web page; ALLOWED_ORIGINS on API must include that exact web origin. Local defaults cover localhost:3000 and 127.0.0.1:3000. Production requires HTTPS and explicit origins.

See [browser verification](docs/testing/browser-accounts.md) and [phase 6 decision](docs/decisions/ADR-0006-browser-accounts.md). Earlier phase descriptions below are historical milestones.

Current phase 5: daily completions and streaks are available through the API at http://127.0.0.1:8002/docs. See [daily completion guide](docs/api/streaks.md) for current/best streaks, timezone rules, immutable history and reconciliation. Today excludes credited daily tasks; Daily keeps them visible. Browser habit screens remain phase 7. Earlier phase descriptions below are historical milestones.

Phase 1 foundation: responsive Next.js landing page, FastAPI liveness, validated configuration, isolated PostgreSQL services and quality checks. Accounts and tasks are planned for later phases.

## Setup

Requires Node 24, npm 11, Python 3.14 and Docker Desktop with Linux engine/Compose. From the repository root in PowerShell:

```powershell
python -m venv apps/api/.venv
apps/api/.venv/Scripts/python -m pip install -r apps/api/requirements.lock
npm ci --prefix apps/web
```

Create a local .env using .env.example only if it does not exist. Set POSTGRES_PASSWORD to a locally generated random password; keep it private and never commit it.

```powershell
docker compose --profile test up -d --wait
```

Development PostgreSQL is localhost:5433, database/user devtreck, persistent named volume. Test PostgreSQL is localhost:5434, database devtreck_test, user devtreck, separate ephemeral storage. Stop safely with `docker compose --profile test stop`. Never remove valuable volumes to repair setup.

## Run

From apps/api:

```powershell
.venv/Scripts/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

In another terminal, from apps/web:

```powershell
npm run dev
```

Web: http://localhost:3000. API: http://127.0.0.1:8000/health. Development API docs: http://127.0.0.1:8000/docs. Health means process liveness, not database readiness.

## Verification

From apps/api:

```powershell
.venv/Scripts/python -m pip check
.venv/Scripts/python -m ruff check .
.venv/Scripts/python -m ruff format --check .
.venv/Scripts/python -m mypy app
.venv/Scripts/python -m pytest
```

From apps/web:

```powershell
npm run lint
npm run typecheck
npm run build
npm start
```

Locks: apps/api/requirements.lock and apps/web/package-lock.json. CI mirrors checks on Linux. Local checks do not imply hosted CI success. Persistence/migrations arrive in phase 2; browser E2E in phase 6; production hosting/TLS/backups in phase 10. No production deployment yet.

See docs/project-planning for prompts, docs/decisions for ADRs, docs/architecture for design and docs/phase-reports for evidence. Keep stable main and private origin; use focused commits on codex/ phase branches. Submit later phase prompts individually.

## Phase 2 persistence foundation

See [database setup/migrations](docs/database/foundation.md), [API/error contract](docs/api/conventions.md) and [phase 2 report](docs/phase-reports/PHASE-02-REPORT.md). API uses apps/api/.env DATABASE_URL; tests use apps/api/.env.test TEST_DATABASE_URL (examples in root .env.example). These local files are ignored. Integration tests require the separate test service and create/drop only random disposable databases.

Run API with `--no-access-log` to keep query strings out of Uvicorn logs. GET /ready checks DB connectivity separately from /health liveness. Apply migrations explicitly; no automatic production migration or schema reset. Accounts are phase 3, not part of this foundation.

## Phase 3: usable account APIs

Registration, login/logout, profile/timezone/theme and email updates, password change and confirmed account deletion are now available through the API. See [account API guide](docs/api/accounts.md) for headers, cookie/CSRF usage and startup on port 8002. Browser account screens are still phase 6; the web currently remains a welcome page.

## Phase 4: usable task/category APIs

Create, read, update, archive, search, filter and sort private tasks; complete/reopen one-time tasks and view preserved history. Manage custom categories without deleting their tasks. API docs remain http://127.0.0.1:8002/docs after restarting the API. [Task API guide](docs/api/tasks.md) documents fields, cookie/CSRF headers, list views and confirmations. Daily tasks can be created, but completion/streaks arrive in phase 5. Browser task screens arrive in phase 7.

## Phase 9: rewards and insights

Open `/app/progress` from Progress navigation for server-owned XP, levels, four achievement milestones, today/seven-date completion and focus summaries, habit consistency and accessible daily/category activity. Existing history is credited once. Rates remain unavailable for zero or incompletely tracked denominators. See [reward/insight contract](docs/api/progress.md), [ADR](docs/decisions/ADR-0009-rewards-insights.md) and [phase report](docs/phase-reports/PHASE-09-REPORT.md). Prior phase sections describe their historical delivery boundaries; Progress is now implemented. External hosting remains phase 10.
