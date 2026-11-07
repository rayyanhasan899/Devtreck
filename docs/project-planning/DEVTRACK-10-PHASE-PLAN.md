# Devtreck ten-phase implementation plan

Planning snapshot: 2026-11-07, Asia/Karachi. Planning only; no features implemented.

## Assessment and source interpretation

Actual checkout: D:/RAYYAN/Projects/Devtreck; only tracked README.md; clean main at b38a609 (first commit); origin https://github.com/rayyanhasan899/Devtreck.git, verified private with GitHub CLI. Only main and origin/main detected. No existing application/tests/config to reuse; preserve README. Supplied sources live in D:/RAYYAN/Devtreck, a different directory. Master instruction is C:/Users/rayya/Downloads/DEVTRACK_CODEX_MASTER_PLANNING_PROMPT.md. The user's request delegates execution of that document; its explicit boundary is planning, not implementation.

Requirements.md defines behavior and acceptance; blueprint is a reusable layering guide, including illustrative projects/payments and optional infrastructure that are not product requirements. Devtrack spelling is not a rename. No blocking source conflict found: section 2 includes productivity features, while section 8 describes them as recommended; include 8.1–8.5 as directed by master scope. Blueprint async setup and /api/v1 are recommendations, not mandatory contradictions with illustrative /api routes; choose and document one contract at implementation.

## Scope and architecture

Initial release: complete accounts, tasks/categories, due dates, status/priority, every listed view, daily streak history, planning, focus, checklists, XP/achievements, insights and complete responsive accessible UI. Optional/deferred: password recovery until real email delivery exists, reminders/notifications, freezes, custom recurrence, integrations, exports, mobile and admin. No nonfunctional notification switches.

Use Next.js/TypeScript/Tailwind and FastAPI/PostgreSQL/SQLAlchemy 2/Alembic. Modular monolith, feature-aware layer organization, thin HTTP/UI, framework-free rules, explicit constructor dependencies/repository ports where useful and application transaction boundaries. No empty architecture scaffolding. Explicit Pydantic contracts/OpenAPI and centralized typed web client. Sync persistence initially; async only with demonstrated benefit and consistent boundaries. PostgreSQL remains the test database for constraints/concurrency.

Recommend cookie-backed revocable sessions with CSRF defense, Argon2id, validated environment configuration, same-origin deployment, owner-scoped services and indexed constraints. Server clocks and recorded IANA zone/local-day facts govern streaks; immutable completion facts support reconciliation. No midnight cron required. No Redis/Celery/microservices/Kubernetes needed. Compose is sufficient for reproducible local development and potentially a single-host release; production needs real TLS, secrets, backups and operations.

Design: slate text/surfaces, restrained teal accents, spacious readable task rows, compact priority indicators with labels, clear typography and persistent add-task affordance. Light/dark/system tokens; desktop sidebar, tablet adaptation and mobile navigation. Semantic dialogs/forms, keyboard controls, visible focus, sufficient contrast and reduced motion. Every completed screen has working controls and loading/empty/error/success states.

## Decisions and questions

No answer blocks this planning delivery. Assumptions.md contains proposed choices, not approvals. Before affected implementation confirm retention/archival, cookie auth, timezone transitions, reopen/reward behavior and analytics formula through ADRs or explicit user direction if materially disputed. Deployment host/domain/budget must be chosen before external release; recommend portable single-host Compose first, with no paid purchase now. Sources need copying into the checkout in phase 1 for fresh-clone reproducibility.

## Roadmap and dependencies

Strict sequence 01 → 02 → 03 → 04 → 05 → 06 → 07 → 08 → 09 → 10. This separates phase 8's three interactive productivity workflows from phase 9's rewards/analytics instead of overloading one phase. Integration/security testing happens throughout; final hardening occurs in phase 10. CI starts in phase 1 and expands continuously.

## Phase 01: Foundation and reproducible development

Objective: Establish the smallest runnable monorepo and verified developer workflow.

Requirements: NFR-14–20; blueprint 17, 29, 32, 42.

Entry/dependencies: Planning reviewed; source files accessible; no installation performed yet.

Backend/application work: Create apps/web and apps/api with only useful layer boundaries; validate configuration and secret-free examples. Verify compatible stable dependencies against official documentation at execution time; pin runtime ranges and lock packages. Retain Node 24 if supported; smoke-test installed Python 3.14 wheels before choosing a separately installed supported Python. Create npm scripts, Python venv, Ruff, pytest and typing configuration. Add minimal GitHub Actions lint/type/build checks. Record ADRs and a restrained visual specification.

Database/migrations: Compose PostgreSQL with persistent development volume and isolated test database; diagnose Docker Desktop before installation. No valuable database reset.

Frontend/UI: Runnable Next.js landing page and FastAPI health endpoint; define typography, spacing, slate surfaces, teal accent, light/dark/system tokens and accessible primitives. No links to unfinished features.

Security/privacy: enforce owner scope, safe validation/logging and the common prompt guardrails; verify changed attack surfaces with negative tests.

Tests and exit criteria: Clean dependency installation, API health, frontend production build, lint and type checks pass; document exact commands and selected versions.

Verification commands: From apps/api with its venv active: python -m pytest; python -m ruff check .; python -m ruff format --check .; python -m mypy app. From apps/web: npm run lint; npm run typecheck; npm run build. Run only tools introduced by this point; establish missing scripts in phase 1. For database phases: python -m alembic upgrade head against disposable test PostgreSQL. For browser phases: npx playwright test. Record actual working directories, commands and outcomes; a missing tool/check is not a passing result.

Documentation: update relevant docs/ADRs and assumptions; create docs/phase-reports/PHASE-01-REPORT.md with evidence and outstanding limitations.

Risks/blockers: Docker engine unavailable; Python wheel compatibility unverified; source documents currently outside the Git checkout.

Possible manual action: Start Docker Desktop and complete any Windows virtualization/restart prompts only if diagnosis requires it.

## Phase 02: Persistence and backend boundaries

Objective: Build reliable PostgreSQL persistence, migrations and test infrastructure.

Requirements: SEC-05–08,11–13; NFR-03–04,07–08,14–17,20–21.

Entry/dependencies: Phase 01 exit criteria passed; read its report and resolve relevant blockers first.

Backend/application work: Implement configuration validation, request-scoped SQLAlchemy 2 sessions, repository ports, application transaction unit, domain error mapping and correlation logging. Choose synchronous SQLAlchemy and sync route handlers initially; document the trade-off and keep blocking work off async paths.

Database/migrations: Alembic initial user/session foundations, normalized email uniqueness and UTC timestamps; migration conventions and owner-aware foreign-key strategy. Validate upgrade on empty PostgreSQL, rollback on failure and schema/model agreement.

Frontend/UI: Document Pydantic/OpenAPI response and error contracts for the centralized client; no feature screens yet.

Security/privacy: enforce owner scope, safe validation/logging and the common prompt guardrails; verify changed attack surfaces with negative tests.

Tests and exit criteria: Real PostgreSQL integration tests prove commit/rollback, constraints, readiness, safe error mapping and secret redaction. Never substitute SQLite for concurrency evidence.

Verification commands: From apps/api with its venv active: python -m pytest; python -m ruff check .; python -m ruff format --check .; python -m mypy app. From apps/web: npm run lint; npm run typecheck; npm run build. Run only tools introduced by this point; establish missing scripts in phase 1. For database phases: python -m alembic upgrade head against disposable test PostgreSQL. For browser phases: npx playwright test. Record actual working directories, commands and outcomes; a missing tool/check is not a passing result.

Documentation: update relevant docs/ADRs and assumptions; create docs/phase-reports/PHASE-02-REPORT.md with evidence and outstanding limitations.

Risks/blockers: Earlier phase defects, schema/contract drift and integration regressions; resolve them or report a specific blocker without claiming completion.

Possible manual action: Only indispensable secure login/approval or a material unresolved decision; deployment target and budget required before external hosting in phase 10.

## Phase 03: Accounts and authentication

Objective: Deliver secure account APIs with complete private-data lifecycle.

Requirements: ACC-01–21; SEC-01–14; requirements 16.1.

Entry/dependencies: Phase 02 exit criteria passed; read its report and resolve relevant blockers first.

Backend/application work: Implement registration, login, logout, me read/update including email, password change and deletion with reauthentication. Argon2id hashes; opaque random revocable server sessions, hashed session tokens in storage, HttpOnly SameSite cookies, production Secure, expiration and CSRF/origin protection. Database-backed sensitive-route throttling; generic invalid-login errors. Reject client owner IDs.

Database/migrations: Add password/session/account constraints, expiry indexes and cascades. Account deletion transaction removes all owned records and sessions; extend as later tables arrive.

Frontend/UI: Publish API contracts and examples; functional auth UI arrives in phase 6. Specify password policy and session lifetime in ADR.

Security/privacy: enforce owner scope, safe validation/logging and the common prompt guardrails; verify changed attack surfaces with negative tests.

Tests and exit criteria: Test normalized duplicate emails, expiration/revocation, CSRF, throttling, password/email change, deletion and cross-account access; no password hashes in responses.

Verification commands: From apps/api with its venv active: python -m pytest; python -m ruff check .; python -m ruff format --check .; python -m mypy app. From apps/web: npm run lint; npm run typecheck; npm run build. Run only tools introduced by this point; establish missing scripts in phase 1. For database phases: python -m alembic upgrade head against disposable test PostgreSQL. For browser phases: npx playwright test. Record actual working directories, commands and outcomes; a missing tool/check is not a passing result.

Documentation: update relevant docs/ADRs and assumptions; create docs/phase-reports/PHASE-03-REPORT.md with evidence and outstanding limitations.

Risks/blockers: Earlier phase defects, schema/contract drift and integration regressions; resolve them or report a specific blocker without claiming completion.

Possible manual action: Only indispensable secure login/approval or a material unresolved decision; deployment target and budget required before external hosting in phase 10.

## Phase 04: Task and category APIs

Objective: Provide owner-scoped task management and explicit lifecycle contracts.

Requirements: TSK-01–22,24–26,28–32; requirements 5–6,12,15; SEC-01–03,06–07.

Entry/dependencies: Phase 03 exit criteria passed; read its report and resolve relevant blockers first.

Backend/application work: Task CRUD, transitions, one-time completion/reopen, categories CRUD with SET NULL semantics, title/description search, allowlisted sorts, filters, bounded pagination. Distinguish date-only due date from an optional due instant; specify overdue behavior. Preserve immutable completion facts on reopen. Do not expose daily completion until phase 5.

Database/migrations: Add tasks, categories and completion facts, indexes by owner/status/due date and history time. Constraints prevent assigning another user category. Record task-type transitions without rewriting history.

Frontend/UI: Update typed API contract specification and task editor field definitions; no fake interactive task pages.

Security/privacy: enforce owner scope, safe validation/logging and the common prompt guardrails; verify changed attack surfaces with negative tests.

Tests and exit criteria: Test all CRUD, invalid identifiers/enums/blank titles, date-only behavior, every view/filter/sort, pagination bounds, category deletion, task-type changes and two-user ownership.

Verification commands: From apps/api with its venv active: python -m pytest; python -m ruff check .; python -m ruff format --check .; python -m mypy app. From apps/web: npm run lint; npm run typecheck; npm run build. Run only tools introduced by this point; establish missing scripts in phase 1. For database phases: python -m alembic upgrade head against disposable test PostgreSQL. For browser phases: npx playwright test. Record actual working directories, commands and outcomes; a missing tool/check is not a passing result.

Documentation: update relevant docs/ADRs and assumptions; create docs/phase-reports/PHASE-04-REPORT.md with evidence and outstanding limitations.

Risks/blockers: Earlier phase defects, schema/contract drift and integration regressions; resolve them or report a specific blocker without claiming completion.

Possible manual action: Only indispensable secure login/approval or a material unresolved decision; deployment target and budget required before external hosting in phase 10.

## Phase 05: Daily completion and streak engine

Objective: Make local-calendar streak history trustworthy under retries and concurrency.

Requirements: STR-01–11; TSK-06,18–19,21,23–24,27; NFR-07–08,15,21; requirements 7,16.3.

Entry/dependencies: Phase 04 exit criteria passed; read its report and resolve relevant blockers first.

Backend/application work: Inject server clock into framework-free streak rules. Completion transaction locks relevant task, determines IANA local date, writes one immutable daily fact and updates derived counters. Current streak is zero after missed yesterday; today pending preserves yesterday streak until day end. One-time tasks never gain streaks. Reopen cannot erase daily credit.

Database/migrations: Unique task/local-day key plus stored UTC timestamp and timezone-at-completion; serialize timezone edits with completions and retain historical dates. Store recurrence activation epochs for type conversions; old history stays visible but a newly enabled daily run begins at zero. Reconciliation derives counters from qualified history.

Frontend/UI: Expose today-completed, last day, current/best and history through contracts. Explain timezone-change effects.

Security/privacy: enforce owner scope, safe validation/logging and the common prompt guardrails; verify changed attack surfaces with negative tests.

Tests and exit criteria: Prove first=1, next=2, duplicates=1, missed reset, best preservation, UTC offsets, midnight, DST spring/fall, timezone changes and concurrent requests using independent PostgreSQL transactions.

Verification commands: From apps/api with its venv active: python -m pytest; python -m ruff check .; python -m ruff format --check .; python -m mypy app. From apps/web: npm run lint; npm run typecheck; npm run build. Run only tools introduced by this point; establish missing scripts in phase 1. For database phases: python -m alembic upgrade head against disposable test PostgreSQL. For browser phases: npx playwright test. Record actual working directories, commands and outcomes; a missing tool/check is not a passing result.

Documentation: update relevant docs/ADRs and assumptions; create docs/phase-reports/PHASE-05-REPORT.md with evidence and outstanding limitations.

Risks/blockers: Earlier phase defects, schema/contract drift and integration regressions; resolve them or report a specific blocker without claiming completion.

Possible manual action: Only indispensable secure login/approval or a material unresolved decision; deployment target and budget required before external hosting in phase 10.

## Phase 06: Frontend system and account experience

Objective: Deliver polished responsive navigation and complete account journeys.

Requirements: UI-05–13; ACC-01–21; NFR-02,05–06,10–13,19; requirements 10.

Entry/dependencies: Phase 05 exit criteria passed; read its report and resolve relevant blockers first.

Backend/application work: Connect existing account APIs without moving business rules into Next.js. Central API client handles credentials, CSRF, errors and expired sessions. Keep secrets server-only.

Database/migrations: No schema changes expected; use reviewed migrations if justified.

Frontend/UI: Landing, signup/login, protected application shell, responsive sidebar/mobile navigation, profile/email/password settings, timezone and theme controls, account-deletion confirmation. Semantic forms, visible focus, contrast, reduced motion, loading/empty/error/success and guarded submissions. Only link completed screens.

Security/privacy: enforce owner scope, safe validation/logging and the common prompt guardrails; verify changed attack surfaces with negative tests.

Tests and exit criteria: Browser tests cover registration/login/logout, session expiry, settings/password/email, deletion and protected navigation. Check keyboard and mobile layouts; run strict TS, lint and production build.

Verification commands: From apps/api with its venv active: python -m pytest; python -m ruff check .; python -m ruff format --check .; python -m mypy app. From apps/web: npm run lint; npm run typecheck; npm run build. Run only tools introduced by this point; establish missing scripts in phase 1. For database phases: python -m alembic upgrade head against disposable test PostgreSQL. For browser phases: npx playwright test. Record actual working directories, commands and outcomes; a missing tool/check is not a passing result.

Documentation: update relevant docs/ADRs and assumptions; create docs/phase-reports/PHASE-06-REPORT.md with evidence and outstanding limitations.

Risks/blockers: Earlier phase defects, schema/contract drift and integration regressions; resolve them or report a specific blocker without claiming completion.

Possible manual action: Only indispensable secure login/approval or a material unresolved decision; deployment target and budget required before external hosting in phase 10.

## Phase 07: Complete core task and dashboard UI

Objective: Make task capture, organization and daily habits usable end to end.

Requirements: TSK-01–32; STR-01–11; UI-01–13; PLN-01; requirements 16.2–16.3.

Entry/dependencies: Phase 06 exit criteria passed; read its report and resolve relevant blockers first.

Backend/application work: Wire task, category, completion and history services; add bounded dashboard aggregate endpoint if needed. Keep all calculations authoritative in backend.

Database/migrations: Only additive indexes/migrations demonstrated necessary by actual queries.

Frontend/UI: All, Today, Upcoming, Overdue, Daily and Completed views; editor/detail, description, categories, duration, dates, status/priority, search/filter/sort/pagination, deletion confirmation and history. Daily view retains completed-today habits; Today work list excludes them. Refresh affected summaries after writes and roll back optimistic failure states.

Security/privacy: enforce owner scope, safe validation/logging and the common prompt guardrails; verify changed attack surfaces with negative tests.

Tests and exit criteria: E2E register → one-time/daily create → edit → filter → complete → streak/history → dashboard → logout. Verify timezone display, two-user privacy, network errors, keyboard use and 360/768/1440 widths.

Verification commands: From apps/api with its venv active: python -m pytest; python -m ruff check .; python -m ruff format --check .; python -m mypy app. From apps/web: npm run lint; npm run typecheck; npm run build. Run only tools introduced by this point; establish missing scripts in phase 1. For database phases: python -m alembic upgrade head against disposable test PostgreSQL. For browser phases: npx playwright test. Record actual working directories, commands and outcomes; a missing tool/check is not a passing result.

Documentation: update relevant docs/ADRs and assumptions; create docs/phase-reports/PHASE-07-REPORT.md with evidence and outstanding limitations.

Risks/blockers: Earlier phase defects, schema/contract drift and integration regressions; resolve them or report a specific blocker without claiming completion.

Possible manual action: Only indispensable secure login/approval or a material unresolved decision; deployment target and budget required before external hosting in phase 10.

## Phase 08: Daily planning, focus and checklists

Objective: Deliver practical planning and persisted focus workflows.

Requirements: PLN-01–06; FOC-01–07; SUB-01–06; SEC-02; NFR-07.

Entry/dependencies: Phase 07 exit criteria passed; read its report and resolve relevant blockers first.

Backend/application work: Daily plan with three top priorities by default, persisted user order, explainable overdue/due/priority/duration ordering and workload estimates with missing estimates labeled. Focus state machine start/pause/resume/stop with server events, elapsed active intervals, task/general association and configurable focus/break preset 25/5. Checklist CRUD/reorder scoped through parent.

Database/migrations: Plan items scoped by owner/local date; one active focus session per user; unique event/idempotency keys and transactional transitions. Store focus/break type and count only active focus intervals. Checklist positions reorder atomically.

Frontend/UI: Today priority and reorder controls with keyboard alternatives; focus timer recovered from backend across refresh/navigation, pause/resume/stop and history; checklist parent progress without automatic parent completion.

Security/privacy: enforce owner scope, safe validation/logging and the common prompt guardrails; verify changed attack surfaces with negative tests.

Tests and exit criteria: Test duplicate/concurrent session commands, refresh recovery, pauses, multi-tab reconciliation, no task auto-completion, cross-owner task/session/checklist IDs, reorder collisions and workload estimates.

Verification commands: From apps/api with its venv active: python -m pytest; python -m ruff check .; python -m ruff format --check .; python -m mypy app. From apps/web: npm run lint; npm run typecheck; npm run build. Run only tools introduced by this point; establish missing scripts in phase 1. For database phases: python -m alembic upgrade head against disposable test PostgreSQL. For browser phases: npx playwright test. Record actual working directories, commands and outcomes; a missing tool/check is not a passing result.

Documentation: update relevant docs/ADRs and assumptions; create docs/phase-reports/PHASE-08-REPORT.md with evidence and outstanding limitations.

Risks/blockers: Earlier phase defects, schema/contract drift and integration regressions; resolve them or report a specific blocker without claiming completion.

Possible manual action: Only indispensable secure login/approval or a material unresolved decision; deployment target and budget required before external hosting in phase 10.

## Phase 09: Rewards and trustworthy insights

Objective: Deliver server-owned motivation and clearly defined analytics.

Requirements: ACH-01–07; INS-01–07; UI-01,06,09–12; requirements 16.4,17.

Entry/dependencies: Phase 08 exit criteria passed; read its report and resolve relevant blockers first.

Backend/application work: Idempotent XP ledger tied to unique source events; backfill earlier valid completions without duplicate grants. Proposed rules: 10 XP one-time first-ever completion, 5 daily qualified day, 5 completed focus session with >=25 active minutes, capped at four focus rewards/day. Level = 1 + floor(XP/100). Badges: first completion, 7-day streak, 25 tasks, 300 focus minutes. Document configurable rules, provenance and anti-toggle behavior.

Database/migrations: Unique ledger source keys and user-achievement constraints. Atomic completion/reward workflow; deletion policy excludes deleted task history from insights while preserving minimal non-content XP ledger until account deletion. Daily occurrence snapshots support stable denominators.

Frontend/UI: Progress page shows XP/next level, badge reason/date, today/trailing-seven-local-date summaries, focus totals, streaks, trends/category breakdown and accessible chart alternatives. Completion rate = completed eligible occurrences / eligible occurrences in displayed period; eligible = due one-time plus active daily occurrences, missing denominator shows unavailable; never count subtasks as task completions.

Security/privacy: enforce owner scope, safe validation/logging and the common prompt guardrails; verify changed attack surfaces with negative tests.

Tests and exit criteria: Test reward retries/concurrency, toggles, backfill, deletion, daily cap, focus eligibility, achievement uniqueness, timezone period bounds and zero denominators. Verify analytics against explicit fixture records.

Verification commands: From apps/api with its venv active: python -m pytest; python -m ruff check .; python -m ruff format --check .; python -m mypy app. From apps/web: npm run lint; npm run typecheck; npm run build. Run only tools introduced by this point; establish missing scripts in phase 1. For database phases: python -m alembic upgrade head against disposable test PostgreSQL. For browser phases: npx playwright test. Record actual working directories, commands and outcomes; a missing tool/check is not a passing result.

Documentation: update relevant docs/ADRs and assumptions; create docs/phase-reports/PHASE-09-REPORT.md with evidence and outstanding limitations.

Risks/blockers: Earlier phase defects, schema/contract drift and integration regressions; resolve them or report a specific blocker without claiming completion.

Possible manual action: Only indispensable secure login/approval or a material unresolved decision; deployment target and budget required before external hosting in phase 10.

## Phase 10: Hardening and release readiness

Objective: Complete integrated verification, production packaging and honest release handover.

Requirements: SEC-01–14; NFR-01–21; requirements 15–17; blueprint 42–43.

Entry/dependencies: Phase 09 exit criteria passed; read its report and resolve relevant blockers first.

Backend/application work: Audit every private endpoint and ownership path; close defects, check query plans/N+1, rate limits, CSRF/CORS, cookies, logs and failure recovery. Finalize CI for PostgreSQL integration, browser E2E, typing/lint, migration and production builds. Container packaging and same-origin reverse proxy with health checks and graceful shutdown.

Database/migrations: Test clean and incremental migrations against disposable PostgreSQL; backup and restore drill with synthetic data, document recovery objectives, retention and forward-fix/rollback procedure. No production migration without approval.

Frontend/UI: Full account/task/streak/planning/focus/reward journey, accessible responsive QA, empty/slow/error states, production smoke test. Remove unfinished controls and misleading estimates.

Security/privacy: enforce owner scope, safe validation/logging and the common prompt guardrails; verify changed attack surfaces with negative tests.

Tests and exit criteria: All required checks pass with recorded evidence and traceability; deployment runbook and secrets checklist complete. Ask for host/domain/budget before external deployment. If unavailable, prove local production stack and report external deployment BLOCKED, never claim live release.

Verification commands: From apps/api with its venv active: python -m pytest; python -m ruff check .; python -m ruff format --check .; python -m mypy app. From apps/web: npm run lint; npm run typecheck; npm run build. Run only tools introduced by this point; establish missing scripts in phase 1. For database phases: python -m alembic upgrade head against disposable test PostgreSQL. For browser phases: npx playwright test. Record actual working directories, commands and outcomes; a missing tool/check is not a passing result.

Documentation: update relevant docs/ADRs and assumptions; create docs/phase-reports/PHASE-10-REPORT.md with evidence and outstanding limitations.

Risks/blockers: Earlier phase defects, schema/contract drift and integration regressions; resolve them or report a specific blocker without claiming completion.

Possible manual action: Only indispensable secure login/approval or a material unresolved decision; deployment target and budget required before external hosting in phase 10.

## Prompt index

- [Phase 01: Foundation and reproducible development](prompts/PHASE-01-PROMPT.md)
- [Phase 02: Persistence and backend boundaries](prompts/PHASE-02-PROMPT.md)
- [Phase 03: Accounts and authentication](prompts/PHASE-03-PROMPT.md)
- [Phase 04: Task and category APIs](prompts/PHASE-04-PROMPT.md)
- [Phase 05: Daily completion and streak engine](prompts/PHASE-05-PROMPT.md)
- [Phase 06: Frontend system and account experience](prompts/PHASE-06-PROMPT.md)
- [Phase 07: Complete core task and dashboard UI](prompts/PHASE-07-PROMPT.md)
- [Phase 08: Daily planning, focus and checklists](prompts/PHASE-08-PROMPT.md)
- [Phase 09: Rewards and trustworthy insights](prompts/PHASE-09-PROMPT.md)
- [Phase 10: Hardening and release readiness](prompts/PHASE-10-PROMPT.md)

## Risks and mitigations

Docker engine unavailable: diagnose/start Desktop before database work; no blind reinstall. Python 3.14 is detected but dependency wheels are unverified: test selected versions in phase 1, install a separately supported version if needed. Avoid declaring latest versions from memory; verify official compatibility at implementation time. Date-only deadlines, timezone moves, task-type conversion and deletion require explicit schema/policy tests. Use real concurrent PostgreSQL requests for completion/reward/focus integrity. Snapshot eligible daily occurrences for historical rates instead of silently recomputing history from current task settings. External deployment depends on an account/target not yet selected. Phase 10 must report a blocked external deployment honestly if unavailable, while finishing local packaging and checks.

## Requirement-to-phase traceability

Requirement IDs are mapped below directly from the supplied baseline. Phases 10 additionally audit all mandatory requirements and acceptance scenarios; implementation reports must add exact code/test references. Optional IDs remain deferred, never marked implemented.

| Requirement | Planned phase(s) | Requirement text |
|---|---|---|
| ACC-01 | 3,6 | The system shall allow a new user to create an account using a name, email address, and password. |
| ACC-02 | 3,6 | The system shall require a valid email format and a password that meets the configured password policy. |
| ACC-03 | 3,6 | The system shall reject registration when the email address is already registered, using a clear and safe error message. |
| ACC-04 | 3,6 | The system shall trim unnecessary whitespace from appropriate text fields and normalize email addresses consistently before checking uniqueness. |
| ACC-05 | 3,6 | The system shall securely hash passwords before storing them. Plain-text passwords shall never be stored or logged. |
| ACC-06 | 3,6 | The system shall validate registration data on both the client and server. |
| ACC-07 | 3,6 | After successful registration, the system shall either sign the user in or direct them to the login screen, according to the implemented flow. |
| ACC-08 | 3,6 | The system shall allow users to log in using their registered email and password. |
| ACC-09 | 3,6 | The system shall verify credentials securely and return a generic error for invalid credentials without disclosing whether an email exists. |
| ACC-10 | 3,6 | The system shall establish an authenticated session using a secure session or token mechanism. |
| ACC-11 | 3,6 | Protected screens and API routes shall require valid authentication. |
| ACC-12 | 3,6 | The system shall allow a user to log out and invalidate or remove the applicable client session credentials. |
| ACC-13 | 3,6 | Expired, invalid, or malformed authentication credentials shall be rejected and the user shall be prompted to authenticate again when appropriate. |
| ACC-14 | 3,6 | The authentication implementation shall use environment variables for secrets and shall not commit secrets to source control. |
| ACC-15 | 3,6 | The user shall be able to view their profile, including name, email, time zone, and selected preferences. |
| ACC-16 | 3,6 | The user shall be able to update permitted profile fields, such as name, time zone, theme, and notification preferences. |
| ACC-17 | 3,6 | A change to the email address shall be validated and shall not conflict with another account. Email verification may be required if email delivery is implemented. |
| ACC-18 | 3,6 | The user shall be able to change their password after providing the required current-password or re-authentication proof. |
| ACC-19 | 3,6 | The user shall be able to request account deletion after an explicit confirmation step. |
| ACC-20 | 3,6 | Account deletion shall delete or irreversibly anonymize the user's personal data, tasks, completion history, and associated records according to the application's stated retention policy. |
| ACC-21 | 3,6 | Users shall not be able to read or modify another user's account or profile by changing an ID in a request. |
| ACC-22 | Deferred optional | If password-reset email delivery is configured, users shall be able to request a time-limited, single-use password-reset link. |
| ACC-23 | Deferred optional | The system shall avoid revealing whether an account exists when a password-reset request is submitted. |
| TSK-01 | 4,5,7 | An authenticated user shall be able to create a task. |
| TSK-02 | 4,5,7 | A task shall require a non-empty title within a documented maximum length. |
| TSK-03 | 4,5,7 | The user shall be able to add an optional description, priority, task type, due date/time, category, estimated duration, and reminder. |
| TSK-04 | 4,5,7 | A new task shall default to `pending` unless the product interface defines another explicit default. |
| TSK-05 | 4,5,7 | New tasks shall be associated with the currently authenticated user on the server. The server shall not trust a client-supplied owner ID. |
| TSK-06 | 4,5,7 | A daily task shall be eligible for streak tracking according to Section 7. |
| TSK-07 | 4,5,7 | The system shall display a success state after a task is created and update the task list without requiring an unnecessary full-page reload. |
| TSK-08 | 4,5,7 | A user shall be able to view all of their active tasks. |
| TSK-09 | 4,5,7 | A user shall be able to view the details of an individual task. |
| TSK-10 | 4,5,7 | A user shall be able to view completed tasks and completion history through a completed/history view. |
| TSK-11 | 4,5,7 | Task queries shall return only records belonging to the authenticated user. |
| TSK-12 | 4,5,7 | The system shall show useful empty states when a user has no tasks or no results match the selected filters. |
| TSK-13 | 4,5,7 | A user shall be able to edit the title and description of their tasks. |
| TSK-14 | 4,5,7 | A user shall be able to update priority, task type, due date/time, category/tags, estimated duration, reminder, and status where applicable. |
| TSK-15 | 4,5,7 | The system shall validate updates on the server and preserve existing values when optional fields are omitted from a partial update. |
| TSK-16 | 4,5,7 | The system shall update the task's modification timestamp after a successful edit. |
| TSK-17 | 4,5,7 | Changing a one-time task into a daily task shall initialize streak tracking without inventing prior completions. |
| TSK-18 | 4,5,7 | Changing a daily task into a one-time task shall stop future streak tracking while retaining or handling historical records according to the product's documented rules. |
| TSK-19 | 4,5,7 | Editing a task's schedule or recurrence settings shall not silently rewrite previously recorded completion dates. |
| TSK-20 | 4,5,7 | A user shall be able to mark a pending or in-progress task as completed. |
| TSK-21 | 4,5,7 | The system shall record the completion time using a trusted server timestamp. |
| TSK-22 | 4,5,7 | Completing a one-time task shall mark it completed and remove it from the default active-task view. |
| TSK-23 | 4,5,7 | Completing a daily task shall create a completion record for the applicable user-local day and update its streak if the day has not already been counted. |
| TSK-24 | 4,5,7 | The interface shall provide a clear way to reopen a task if reopening is supported. Reopening a task shall not silently erase a legitimate historical completion record. |
| TSK-25 | 4,5,7 | A user shall be able to delete their own task after an intentional action; irreversible deletion should have a confirmation or an undo option. |
| TSK-26 | 4,5,7 | Deleting a task shall not delete or affect another user's records. |
| TSK-27 | 4,5,7 | The server shall reject duplicate completion submissions for the same task and user-local day for streak purposes. |
| TSK-28 | 4,5,7 | Users shall be able to search tasks by title and, where practical, description. |
| TSK-29 | 4,5,7 | Users shall be able to filter by status, task type, priority, category/tag, due date, and overdue state. |
| TSK-30 | 4,5,7 | Users shall be able to sort by due date, priority, creation date, updated date, and title. |
| TSK-31 | 4,5,7 | Users shall be able to switch between useful views such as All, Today, Upcoming, Overdue, Daily Tasks, and Completed. |
| TSK-32 | 4,5,7 | Search, filtering, and sorting shall operate only on the current user's authorized task set. |
| STR-01 | 5,7 | Only tasks configured as daily recurring tasks shall have a streak. |
| STR-02 | 5,7 | A daily task shall have a streak counter, best streak, and completion history. |
| STR-03 | 5,7 | A qualifying completion shall count for the user's local calendar day, determined by the user's configured time zone. |
| STR-04 | 5,7 | The user must complete the daily task before the next local midnight to receive credit for that day. For example, a task due for October 2 must be completed before the start of October 3 in the user's time zone. |
| STR-05 | 5,7 | A task shall count at most one completion per local calendar day. Multiple completions or duplicate requests on one day shall not raise the streak more than once. |
| STR-06 | 5,7 | If a task is completed on the next consecutive calendar day, its current streak shall increase by one. |
| STR-07 | 5,7 | If a task misses an eligible calendar day, its current streak shall reset according to the streak definition. The best streak shall remain unchanged. |
| STR-08 | 5,7 | The system shall show the current streak and best streak for every eligible task. |
| STR-09 | 5,7 | The system shall show the most recent qualifying completion date and whether today's task has been completed. |
| STR-10 | 5,7 | Streak calculations shall be based on completion-history records and reliable timestamps, not merely on a client-side counter. |
| STR-11 | 5,7 | Concurrent or repeated requests shall not create duplicate daily completion records or inconsistent streak totals. |
| STR-12 | Deferred optional | The product may offer a limited Streak Freeze that protects a missed day. If implemented, the allowance, eligibility, and effect on the streak must be clearly displayed and applied consistently. |
| STR-13 | Deferred optional | Users must not be able to repeatedly exploit freeze or recovery actions to produce unlimited streak credit. Any use should be recorded in the task's history. |
| PLN-01 | 7,8 | Provide a Today view containing tasks due today, overdue tasks, and daily tasks not yet completed today. |
| PLN-02 | 7,8 | Allow users to mark a small number of tasks as their top priorities for the day. |
| PLN-03 | 7,8 | Offer a suggested order based on due date, priority, overdue status, and estimated duration. |
| PLN-04 | 7,8 | Explain or make visible why a task is suggested, such as “high priority” or “due today.” |
| PLN-05 | 7,8 | Let the user override the suggested order. The application shall assist the user rather than force a plan. |
| PLN-06 | 7,8 | If estimated durations are present, display an approximate total planned workload for the day. |
| FOC-01 | 8 | Users shall be able to start a focus session associated with a task or with a general focus activity. |
| FOC-02 | 8 | Provide a configurable work timer and break timer. A standard preset such as 25 minutes of focus and 5 minutes of break may be offered. |
| FOC-03 | 8 | Allow a user to pause, resume, or stop a session. |
| FOC-04 | 8 | Record session start, end, duration, associated task, and completion state. |
| FOC-05 | 8 | Display daily and weekly focus time in the user's statistics. |
| FOC-06 | 8 | A timer ending shall not automatically mark its associated task complete. |
| FOC-07 | 8 | Timer state should remain understandable if the user navigates to another screen or refreshes the page. The backend should record session events where necessary to avoid relying entirely on a running browser timer. |
| ACH-01 | 9 | Award XP for valid task completions and completed focus sessions using clearly defined, configurable rules. |
| ACH-02 | 9 | Avoid awarding duplicate XP for duplicate requests or repeatedly toggling a task between complete and incomplete. |
| ACH-03 | 9 | Provide levels based on accumulated XP and show the user's current level and progress to the next level. |
| ACH-04 | 9 | Provide achievements or badges for milestones, such as completing the first task, reaching a streak milestone, finishing a number of tasks, or accumulating focus time. |
| ACH-05 | 9 | Show the reason and date when an achievement is earned. |
| ACH-06 | 9 | Recompute or validate rewards on the server so users cannot grant themselves arbitrary XP by altering client requests. |
| ACH-07 | 9 | Reward rules shall be transparent and shall not encourage users to create meaningless duplicate tasks merely to gain points. |
| INS-01 | 9 | Show tasks completed today and over the last 7 days. |
| INS-02 | 9 | Show task completion rate for a clearly specified period and define the calculation used. |
| INS-03 | 9 | Show current and best streaks, total daily-task completions, and streak milestones. |
| INS-04 | 9 | Show total focus time and session count for the selected period when focus sessions are enabled. |
| INS-05 | 9 | Show completion trends by day and, where categories exist, by category. |
| INS-06 | 9 | Distinguish actual recorded data from estimates and avoid presenting insufficient data as a meaningful trend. |
| INS-07 | 9 | All analytics shall be scoped to the signed-in user. |
| SUB-01 | 8 | Users may add checklist items or subtasks to a parent task. |
| SUB-02 | 8 | Each checklist item shall have a title and completion state. |
| SUB-03 | 8 | Users shall be able to add, edit, reorder, complete, and delete checklist items they own through the parent task. |
| SUB-04 | 8 | Display checklist progress, such as “3 of 5 complete,” on the task card or detail view. |
| SUB-05 | 8 | Completing all checklist items shall not automatically complete the parent task unless that behavior is explicitly enabled and communicated. |
| SUB-06 | 8 | Subtasks shall inherit access control from their parent task and shall not be accessible independently to another user. |
| NOT-01 | Deferred optional | Users may configure reminders for tasks with due dates or for daily tasks. |
| NOT-02 | Deferred optional | Reminders shall respect the user's time zone and notification preferences. |
| NOT-03 | Deferred optional | Users shall be able to enable or disable each supported notification channel. |
| NOT-04 | Deferred optional | If push or email delivery is not configured, the application shall not imply that an external notification was sent; in-app reminders may be used instead. |
| NOT-05 | Deferred optional | Notifications should avoid sending repeated or duplicate reminders for the same task occurrence. |
| UI-01 | 6,7,8,9 | The dashboard shall show a summary of today's tasks, completed tasks, outstanding tasks, and daily streaks. |
| UI-02 | 6,7,8,9 | The primary task list shall make task title, status, priority, due date, and daily streak easy to scan. |
| UI-03 | 6,7,8,9 | Daily tasks shall visibly indicate whether they have been completed today and show their current streak. |
| UI-04 | 6,7,8,9 | Provide clear, consistent actions for adding a task, editing a task, marking it complete, and deleting it. |
| UI-05 | 6,7,8,9 | Use confirmation or undo behavior for destructive actions. |
| UI-06 | 6,7,8,9 | Provide loading, success, empty, and error states for asynchronous operations. |
| UI-07 | 6,7,8,9 | Prevent accidental multiple submissions by disabling or guarding actions while a request is in progress, without relying on the interface as the only duplicate protection. |
| UI-08 | 6,7,8,9 | Forms shall identify required fields and explain validation errors near the relevant input. |
| UI-09 | 6,7,8,9 | The interface shall be responsive at common desktop, tablet, and mobile viewport sizes. |
| UI-10 | 6,7,8,9 | Provide keyboard-accessible navigation and visible focus states for interactive controls. |
| UI-11 | 6,7,8,9 | Use sufficient color contrast and do not communicate task status, priority, or streak state through color alone. |
| UI-12 | 6,7,8,9 | Dates and times shall be displayed consistently using the user's chosen time zone. |
| UI-13 | 6,7,8,9 | Provide a settings screen for profile, time zone, theme, and applicable notification preferences. |
| SEC-01 | 2–10 | Enforce authentication on every private API route. |
| SEC-02 | 2–10 | Enforce ownership authorization on every task, category, completion, focus session, subtask, and user-achievement operation. |
| SEC-03 | 2–10 | Never rely solely on a client-provided user ID to determine data ownership. |
| SEC-04 | 2–10 | Hash passwords using a modern password-hashing algorithm with appropriate parameters. |
| SEC-05 | 2–10 | Keep signing keys, database credentials, email credentials, and other secrets in environment variables or a managed secret store. |
| SEC-06 | 2–10 | Validate and normalize incoming input on the server, including IDs, lengths, enums, timestamps, filters, and pagination parameters. |
| SEC-07 | 2–10 | Use safe database queries and prevent injection vulnerabilities. |
| SEC-08 | 2–10 | Configure CORS for approved frontend origins rather than allowing arbitrary origins in production without a deliberate reason. |
| SEC-09 | 2–10 | Use HTTPS in production and secure cookie settings if cookie-based authentication is selected. |
| SEC-10 | 2–10 | Apply rate limiting to sensitive endpoints such as login, registration, and password recovery. |
| SEC-11 | 2–10 | Do not log passwords, authentication tokens, password-reset tokens, or sensitive personal information. |
| SEC-12 | 2–10 | Return only fields the client is authorized to see; never return password hashes in profile responses. |
| SEC-13 | 2–10 | Use safe error messages that do not reveal secrets, internal stack traces, or unnecessary account information. |
| SEC-14 | 2–10 | Account deletion shall include associated user-owned records and any applicable external data, subject to the documented retention policy. |
| NFR-01 | 1–10 | Common actions such as opening the task list, checking off a task, and viewing today's dashboard should feel responsive under normal operating conditions. |
| NFR-02 | 1–10 | The application shall avoid unnecessary full-page reloads for routine CRUD actions. |
| NFR-03 | 1–10 | Database queries for a user's tasks and completion history shall be appropriately indexed for expected access patterns. |
| NFR-04 | 1–10 | Lists with large numbers of records shall use pagination, limits, or another scalable loading strategy. |
| NFR-05 | 1–10 | Task creation, updates, completion, and deletion shall provide clear success or failure feedback. |
| NFR-06 | 1–10 | Failed requests shall not leave the client displaying an unconfirmed change as if it were saved. |
| NFR-07 | 1–10 | Streak, completion, and XP updates shall be consistent under retry, duplicate, and concurrent requests. |
| NFR-08 | 1–10 | The system shall preserve completion history reliably enough to recalculate streaks and analytics if cached counters become inconsistent. |
| NFR-09 | 1–10 | Production data should be backed up according to the deployment's recovery requirements. |
| NFR-10 | 1–10 | Core task actions shall require minimal navigation and be usable on a narrow mobile screen. |
| NFR-11 | 1–10 | Forms shall provide understandable validation messages. |
| NFR-12 | 1–10 | Interactive controls shall be keyboard accessible and should use appropriate labels and semantic elements. |
| NFR-13 | 1–10 | The interface shall remain understandable without relying exclusively on color, animation, or icons. |
| NFR-14 | 1–10 | Separate interface, API/controller, business-logic/service, data-model, and validation responsibilities where appropriate. |
| NFR-15 | 1–10 | Keep streak calculations and reward rules in testable backend business logic rather than duplicating them across UI components. |
| NFR-16 | 1–10 | Use consistent naming, formatting, error handling, and API response conventions. |
| NFR-17 | 1–10 | Document environment variables, installation, development commands, database setup, and deployment configuration. |
| NFR-18 | 1–10 | Include automated tests for critical account, task, authorization, and streak behavior. |
| NFR-19 | 1–10 | Support current major desktop and mobile browsers. |
| NFR-20 | 1–10 | Keep environment-specific configuration outside source code. |
| NFR-21 | 1–10 | Dates must be stored and processed consistently (normally UTC timestamps plus the user's IANA time zone and the qualifying local completion date). |

Unnumbered coverage: requirements §§1–3 scope/privacy (all phases); §5 task fields and §6 lifecycle/categories (4,5,7); §7.2–7.4 streak examples (5); §10 all screens (6–9); §11 entities (2–5,8–9); §12 endpoint groups (3–5,8–9); §15 validation/errors (2–10); §16 all acceptance scenarios and §17 unit/API/E2E tests (feature phases plus 10); §18 priorities (core before productivity); §19 decisions (Assumptions and feature ADRs). Blueprint §§1–48 supplies architecture/workflow guardrails across all phases, not extra product entities.
