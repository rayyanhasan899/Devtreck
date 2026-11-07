# Phase 02 report — Persistence and backend boundaries

Date: 2026-11-07, Asia/Karachi. Status: **PASS WITH KNOWN LIMITATIONS**.

## Objective, scope and implemented behavior

Reliable PostgreSQL persistence foundation: explicit SQLAlchemy request-scoped sessions with rollback/close cleanup; bounded engine with connection timeout, pre-ping and UTC option; typed repository/UoW ports; framework-free User and errors; explicit commit/rollback including recovery after failed commits. User/session models and reviewed Alembic revision 496d77b4d913 provide normalized unique email, UTC-aware timestamps, token-hash uniqueness, owner FK/cascade, positive session lifetime and indexes.

Public /ready checks database connectivity independently of /health liveness. Error envelopes and OpenAPI models provide safe 404/409/422/500/503 responses and matching X-Request-ID. Fresh server IDs ignore untrusted incoming IDs. Structured application logs omit query strings, bodies, tokens, SQL exception contents and account values. Uvicorn must use --no-access-log to avoid default URL/query access logs. Configuration uses SecretStr, hides validation inputs, requires PostgreSQL psycopg and requires database configuration in production.

No account/authentication endpoints, password hashing implementation, tasks, feature screens or full account validation are claimed. Those start in phase 3.

## Requirements and files

Contributions: SEC-05 configuration privacy, SEC-06 safe validation/errors, SEC-07 ORM parameter handling, SEC-08 no permissive CORS, SEC-11–13 redaction/safe contracts; NFR-03–04 schema/index foundations, NFR-07–08 transactions/history foundations, NFR-14–17 boundaries/contracts/docs, NFR-20–21 configuration/timezone-aware persistence. Complete product satisfaction remains dependent on later features.

Added apps/api/alembic.ini; database base/session/migrations; domain User/errors; services ports; persistence models/UoW; presentation error models/handlers; PostgreSQL integration tests. Modified API configuration/main/health and foundation tests. Extended .env.example and GitHub Actions PostgreSQL integration job. Added database/API docs and ADR-0002; updated README/Assumptions. No user files deleted; no dependency versions changed.

ADRs explain sync handlers and application transaction boundaries, lifecycle ownership and production/test privilege separation. Assumptions A-07 implemented; A-17–20 record foundational schema, disposable database role, email normalization and contract shape. Cookie-session strategy remains proposed, not a completed auth decision.

## Tools, commands and actual verification

Used existing Python 3.14.7, SQLAlchemy 2.1.8, Alembic 1.20.1, psycopg 3.3.8, pytest 9.2.0, Ruff 0.17.4, mypy 2.4.1, PostgreSQL 18.6 and Node 24.15.0; existing lockfiles unchanged. Official SQLAlchemy session and Alembic tutorial documentation checked.

From apps/api:

- python -m ruff check .: passed.
- python -m ruff format --check .: 22 files formatted, passed.
- python -m mypy app: 20 source files, passed.
- python -m pytest: **15 passed**, no skips or warnings.
- python -m pip check: no broken requirements.
- Integration fixture executed Alembic upgrade head on a fresh random database, downgrade base, re-upgrade head and alembic check: passed, no schema drift.
- Verified local development additive migration with python -m alembic upgrade head, current and check after disposable tests passed.

Integration evidence: committed row visible, rolled-back row absent, failed duplicate/normalization commit rolls back and session recovers, concurrent same-email writes produce one commit/one duplicate, invalid owner FK fails, owner deletion cascades sessions, timestamp UTC offset zero, uncommitted request flush is rolled back, and transactional DDL failure leaves no probe table. Readiness tests exercise connected, misconfigured and unreachable databases. Error tests exercise database, domain, HTTP, validation and unexpected failures; synthetic secret absent from bodies/logs and response ID matches header.

From apps/web: npm run lint, npm run typecheck and npm run build all passed. No frontend source changed. Live updated API on 127.0.0.1:8001 returned /ready HTTP 200 with correlation header. Docker services remained healthy. git diff --check passed; API-local .env/.env.test are confirmed ignored.

## Failures and resolutions

An initial file-generation command used the wrong working directory and made no intended changes; corrected path and reran. Ruff requested narrowed configuration exception handling/import formatting; fixed and reran. Alembic warned about missing path_separator; configured os separator and reran without warnings. No unresolved test failure.

## Security, integrity and limits

Root credentials were read locally to generate ignored API config without printing secrets. Tests require configured database name devtreck_test, create only random devtreck_verify_<uuid> databases, and drop only those generated disposable databases on teardown. Existing data is never reset. Local development received additive tables only; no production connection, migration or destructive operation. CI test role CREATEDB privilege must never be granted to production app role.

Known limitations: GitHub workflow authored but not remotely run; Linux execution is not claimed. Readiness checks connectivity only, not schema revision. Full owner authorization, password/session security, IANA zone/theme validation and normalized input workflows remain phase 3. PostgreSQL DDL failure simulation is not a production recovery drill. Future field-level validation should add safe details for UI without echoing credentials. No deployment/push/PR performed.

## Git, manual actions and handover

Branch codex/phase-02 continues verified phase 1 history. Commits: 4dc7777 persistence/migration/tests; bd57c2f PostgreSQL CI; final documentation commit visible in git log. Existing origin and main preserved. No force/reset/clean/history rewrite.

No manual action needed. API-local configuration is ready and database services are running. Updated API is available on port 8001 for inspection; older phase-1 API on 8000 may still be running and must be restarted to serve updated code. README contains normal startup commands. Phase 2 local exit criteria met; stop here and await PHASE-03-PROMPT.md.
