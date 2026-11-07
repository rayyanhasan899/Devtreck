# Devtreck implementation prompt — phase 05

Read the actual repository before editing. Project: Devtreck; stack: Next.js, TypeScript, Tailwind, FastAPI, PostgreSQL, SQLAlchemy 2 and Alembic; modular layered monolith. Read Requirements.md and DEVTRACK_ARCHITECTURE_BLUEPRINT.md (if absent locally, use D:/RAYYAN/Devtreck/Requirements.md and D:/RAYYAN/Devtreck/DEVTRACK_ARCHITECTURE_BLUEPRINT.md), root Assumptions.md, docs/project-planning/DEVTRACK-10-PHASE-PLAN.md and all relevant prior phase reports. Source requirements govern product behavior; blueprint examples are guidance. Inspect installed versions again and verify current compatibility from official sources before selecting dependencies.

Check git status, branch, history and remote; preserve user changes and existing origin. Work on codex/phase-05 or a safe existing feature branch, with integration through develop and PRs to main where supported. Never overwrite unrelated work, reset/clean, rewrite history, force-push, replace remotes, expose the private repo or run destructive valuable-data operations. Commit verified milestones when safe; push/PR only when permitted and checks pass. Do not automatically merge to main.

Implement this phase end to end, install/configure safe required dependencies when possible, run the app, run checks, diagnose and fix failures. Continue independent work when blocked. Ask only for indispensable product/data decisions, secure sign-in, privileged authorization, paid/external choices or destructive actions. Never request secrets in chat; use secure local/official flows. Do not commit .env, credentials, keys or dumps. Apply server authorization to every owned resource and transactions/constraints to integrity rules; no client-trusted counters. Keep Pydantic, domain and ORM responsibilities separate and frontend API calls centralized.

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

Update README and relevant architecture/API/database/setup/testing/deployment docs, requirement-to-code/test traceability, ADRs and Assumptions.md. Write docs/phase-reports/PHASE-05-REPORT.md with objective/scope; requirement IDs; files created/changed/deleted; actual behaviors; design decisions; assumptions and approval status; commands/tool versions; actual test outcomes; failures and resolutions; deferred/incomplete work; security/integrity implications; branch/commit/push/PR status; exact manual actions; status PASS, PASS WITH KNOWN LIMITATIONS, BLOCKED or NOT COMPLETE. Never invent tests, coverage, screenshots, commits or deployment evidence. Do not pass unmet mandatory acceptance criteria. Stop at this phase boundary and await the next prompt. Final handover: what works, evidence, failures, remaining work/manual actions, Git state and exit-criteria result.
