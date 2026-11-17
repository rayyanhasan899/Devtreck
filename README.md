# Devtreck

A full-stack productivity application built with **Python/FastAPI**, **TypeScript/Next.js**, React and PostgreSQL. Organize tasks and habits, plan daily priorities, track focus sessions and review progress in one account-scoped workspace.

[Open Devtreck](https://devtreck.vercel.app) · [Release runbook](docs/deployment/RUNBOOK.md) · [Architecture decisions](docs/decisions) · [Verification evidence](docs/testing/release-readiness.md)

## Features

- Account registration, session authentication, profile/settings and confirmed deletion.
- Private tasks and categories with search, filters, history and daily habit streaks.
- Daily priorities, ordered checklists and configurable focus/break sessions with recovery.
- Server-owned XP, levels, achievements and progress insights; unknown historical denominators remain unavailable.

## Engineering focus

FastAPI services and repositories enforce account ownership, validated API contracts and transactional data rules. PostgreSQL/Alembic manage persistence and migrations. The React frontend uses a same-origin API path with cookie sessions and CSRF checks. See [account APIs](docs/api/accounts.md), [productivity](docs/api/productivity.md) and [progress rules](docs/api/progress.md).

## Deployment and evidence

The recorded release uses Vercel Hobby for frontend/API and Neon Free PostgreSQL. The [phase 10 report](docs/phase-reports/PHASE-10-REPORT.md) records 73 API regression tests and a hosted browser journey covering accounts, tasks, habits, checklists, focus, progress and account cleanup. These are recorded results, not tests rerun by this documentation update. GitHub source and deployed revisions can differ.

Personal/non-commercial use only under the documented Hobby hosting arrangement. Free quotas and cold starts may interrupt availability. Automated off-provider backups, password recovery, external notifications and custom recurrence remain outside the delivered scope. No uptime or production-scale performance guarantee is claimed. See [hosting limits](docs/deployment/FREE-HOSTING.md).

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
.venv/Scripts/python -m uvicorn app.main:app --host 127.0.0.1 --port 8002 --reload
```

In another terminal, from apps/web:

```powershell
npm run dev
```

Web: http://localhost:3000. API: http://127.0.0.1:8002/health. Development API docs: http://127.0.0.1:8002/docs. Health means process liveness, not database readiness.

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

Lockfiles: `apps/api/requirements.lock` and `apps/web/package-lock.json`. Integration tests require the separate disposable test database; never point them at personal or production data. Apply migrations explicitly using the [database guide](docs/database/foundation.md). Never reset valuable volumes to repair setup.

## Project records

[Phase reports](docs/phase-reports) preserve delivery history and actual validation outcomes; [planning records](docs/project-planning) preserve the project's development context. Earlier phase descriptions are historical, not a list of current missing features. No license is added by this portfolio update.
