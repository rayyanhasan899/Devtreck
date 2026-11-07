# Phase10 report — hardening and release readiness

Date:2026-11-07, Asia/Karachi. **Phase10: PASS WITH KNOWN LIMITATIONS. Live personal deployment: VERIFIED.** Open https://devtreck.vercel.app. Local and hosted journeys pass. No paid resource or automated external backup schedule was activated.

## Scope, requirements and user decisions

Audited SEC-01–14, NFR-01–21 and requirements15–17/blueprint42–43 against existing account/task/streak/planning/focus/reward code and earlier evidence. The submitted phase prompt was executed within the user's request; source requirements govern behavior and blueprint examples remain guidance. Detailed requirement-to-code/test mapping and private-route matrix: docs/testing/release-readiness.md and docs/architecture/phase-01-traceability.md.

User selected Vercel Hobby frontend, Render Free FastAPI only, Neon Free PostgreSQL, free subdomains and strict $0/month. A later statement mentioning business use was superseded by the final explicit **personal-use-only for now** decision, so Vercel Hobby is eligible on that basis. Commercial use must be reconsidered before changing purpose; Netlify Free was reviewed as an alternative. No paid tier, paid trial/card-required flow, custom domain or usage-based spending is authorized.

Official plan/compatibility sources were checked and linked in docs/deployment/FREE-HOSTING.md. Free-tier sleep/quotas/suspensions are explicit; no always-on production SLA. Current Neon live documentation lists1GB/project, while older cached summaries say0.5GB; the guide records the discrepancy and a conservative operating ceiling. Actual Vercel Hobby and Neon Free account plans were subsequently verified; final topology and conservative quotas are recorded below.

## Delivered changes

- API: bounded concurrent Argon2 hashing/verification (two operations per process; safe503 without partial registration), sanitized unexpected failures before Uvicorn traceback logging, request IDs/no-store preserved on500 and nosniff headers. Existing cookies, Origin/CSRF, ownership, source uniqueness and cascades retained. Daily eligibility inserts now batch500 rather than one write per task/date.
- Packaging: digest-pinned multi-stage Python/Next Dockerfiles and secret-excluding contexts; standalone output only in container builds; ordinary Windows build/start remains. Local HTTPS Caddy proxy with128KB request cap, security headers, no request objects in error logs, API upstream connection reuse disabled and bounded connection/header timeouts.
- Isolated release Compose project: only loopback8443 exposed; non-root/read-only API/web, private DB/API/web network, health gating, one-shot owner-role migration, restricted app role, init, shutdown grace and restart policies. Existing development/test database services and data remain separate. No new schema revision; head remains8022c27c58ae.
- Repeatable helpers: exclusive ignored credential generation, synthetic clean/incremental migration + pg_dump/restore drill and TLS/proxy/role/outage/log checks. Generated DB names are validated; only the helper's own databases/dump are removed.
- CI: existing real PostgreSQL API/migration, web lint/type/build and isolated browser jobs retained. Added Linux Docker release job with readiness, recovery, TLS/security/outage and production browser journey, with cleanup and branch concurrency. It is committed but **not run on hosted CI**.
- Prepared render.yaml: explicit Free Docker service, no Render database/disk, auto-deploy off, runtime secrets unset for secure configuration, no publicly trusted forwarded headers. Not submitted to Render and no service created.

Created .gitattributes; API/web Dockerfiles and .dockerignore files; deploy/Caddyfile, compose.release.yaml, init-app-role.sh; render.yaml; scripts/release_env.py, recovery_drill.py, release_checks.py; API tests/test_release.py; web playwright.release.config.ts and release-tests/release.spec.ts; ADR0010; deployment/runbook/free-hosting and testing audit docs; this report. Modified .gitignore/CI, API security/main/accounts/progress persistence+service, Next config, README, assumptions, setup/database/API/testing/traceability docs. No files deleted. The three earlier password-policy source edits remain unstaged and excluded from phase commits.

## Actual verification

Working directory `D:\RAYYAN\Projects\Devtreck\apps\api`, venv Python:

- `python -m pytest`: **73 passed in63.54s** (final rerun after explicit TLS CA fix), including five release-specific tests. Real isolated PostgreSQL; no skipped acceptance tests. Existing fixture covers clean head, base/head round trip, transactional DDL and metadata agreement.
- `python -m ruff check .`: all checks passed. `python -m ruff format --check .`:54 files formatted. `python -m mypy app`: no issues in45 source files. `python -m pip check`: no broken requirements. Scripts separately pass root `apps/api/.venv/Scripts/python -m ruff check scripts` and format check (3files).
- Final `python scripts/browser_checks.py`: **7 passed in58.4seconds**, after final authentication hardening. Account lifecycle/privacy, task/category/habit/streak, planning/checklist/focus recovery, Progress/XP, error recovery, responsive and accessibility journeys. The runner invokes Playwright against generated disposable DB and temporary services; own resources cleaned.

Working directory `D:\RAYYAN\Projects\Devtreck\apps\web`: `npm run lint`, `npm run typecheck`, `npm run build` passed. Changed frontend/release test files pass Prettier check. Normal production build includes all protected routes; separate Linux Docker standalone build also passed. npm ci's built-in audit reported0 vulnerabilities, which is not a comprehensive security scan. It emitted an ESLint9 deprecation notice; tooling remains pinned/working, with a future upgrade requiring compatibility testing.

Working directory repository root:

- `python scripts/release_env.py`: generated ignored local credentials without printing values; refuses overwrite by design.
- `docker compose --env-file deploy/.env.release -f deploy/compose.release.yaml build`: API/web builds passed using pinned base digests and existing locks. No env files copied into images.
- `docker compose ... up -d --wait`: DB, migration one-shot, API, web and proxy health gates passed. Long-running services healthy after verification.
- `apps/api/.venv/Scripts/python scripts/recovery_drill.py`: final **PASS**, clean baseline through phase8 then incremental head, metadata checks, custom-format dump and new-DB restore. All18 tables populated/checked including type-change audit, sessions, focus intervals, plans, occurrences, XP and achievements; every full-row checksum matches. **0 synthetic records lost; restore+verification3.77seconds.** Both generated databases and temporary dump cleaned; actual source/recovery content was synthetic, not a development/production dump.
- `apps/api/.venv/Scripts/python scripts/release_checks.py`: final **PASS** with private-CA TLS verification,128KB rejection413, anonymous/no-store/nosniff/HSTS, spoofed forwarding headers unable to change throttling identity, non-root apps/no env file, restricted runtime role and deliberate API stop502/recovery200. Synthetic query/header marker omitted from proxy error logs. Restricted role check shows no superuser/createdb/createrole/schema-create privileges.
- From apps/web `npx playwright test --config playwright.release.config.ts`: final **1 passed in11.7seconds** against the final production HTTPS stack. UI signup/login, Secure/HttpOnly/SameSiteStrict cookie, task/habit/checklist records, plan navigation, focus pause/reload/stop,15XP, axe0violations,360px overflow check, Origin/CSRF rejection and confirmed account deletion. Normal suite provides768/1440 and broader CRUD coverage. Desktop/mobile production screenshots visually inspected and copied to ignored root .release-results before the normal suite cleaned test-results.
- Caddy configuration validated. Local Docker DB/runtime role and image process UID checked. HTTP smoke of ordinary production web/API retained200login/readiness, private401 and protected-login redirect. Ordinary local servers refreshed after code/build changes.

Query test seeded120 daily tasks/facts and confirmed equal SELECT counts at25/100 returned rows (no list rendering N+1). EXPLAIN with sequential scans disabled confirms owner/archive index usability; not an actual production optimizer/load benchmark. Isolated Argon2 verification in the API container measured0.15seconds during diagnosis; not a free-provider latency guarantee.

Versions: Python3.14.7, Node24.15.0/npm11.12.1, Next16.4.5/React19.3.0, SQLAlchemy2.1.8, PostgreSQL18.6, psycopg-linked libpq18.6, Caddy2.11.9, Docker29.3.1/Compose5.1.1. Python/Node/PostgreSQL/Caddy images pinned by inspected immutable digests. Installed Next standalone documentation read; official Next self-hosting, Docker, Caddy proxy/logging/TLS and provider plan references reviewed before packaging. The existing locked certifi2026.10.23 was made an explicit runtime dependency for managed PostgreSQL certificate verification; no dependency version upgrade was introduced.

## Failures and resolutions

Lint initially required documenting the intentional broad outer exception boundary; added targeted explanation and passed lint/types. Production test initially expected the navigation label as its heading; corrected to the actual Plan your day heading.

Early browser attempts overlapped an intentional API shutdown/recreation and failed with502/disconnected requests. Verification is now explicitly sequential; the final production and regular journeys pass. Local DB briefly reinitialized/entered recovery during the refresh, causing a generated-DB creation attempt to fail. It recovered; no generated database was left behind. The cause was not established, so resource pressure is not asserted as proven. Retried only after readiness; final dump/restore checksums and all health gates passed. No valuable database reset/downgrade occurred.

Subsequent strict10-second TLS checks exposed delayed login responses after the oversized-body probe. Direct API hashing was fast; disabled API upstream reuse and set bounded transport timeouts, then reran TLS/security/outage and production journey successfully. Root-cause attribution beyond the observed proxy/upstream behavior is not claimed. Caddy's read-only mount correctly rejected an in-container overwrite formatting attempt; formatted via captured output to the repository instead. Configuration validation succeeds.

## Verified external deployment

The user explicitly authorized end-to-end deployment, personal-only use, free subdomains and strict $0, and completed secure Vercel/Render device sign-ins. Neon integration worked. Earlier access failures were resolved by official CLI/API flows; credentials never went into chat/Git. Private GitHub origin/visibility preserved.

Final topology: **Vercel Hobby frontend + Vercel Hobby FastAPI + Neon Free PostgreSQL**. The Render alternative was replaced after explaining that its public API could not establish the required zero-spend billing safeguards. Official Vercel FastAPI/Python3.14 support was verified and then tested. No Render service, database or disk was created; render.yaml is an unused prepared alternative. Both apps share one Hobby team allowance. No paid upgrade/trial/add-on/card entry/domain purchase was activated.

- Frontend https://devtreck.vercel.app, project devtreck, Node24, deployment dpl_5euCUktAT1qTAsPd8sqTGocAytwP READY.
- Backend https://devtreck-api.vercel.app, project devtreck-api, Python3.14, fra1, maxDuration60seconds, deployment dpl_ATJvauDPXhnTuC8NkK8syHRtaqBx READY. Public /ready returned200 with database access.
- Actual Vercel team raan-899 plan Hobby; Neon organization plan Free. Neon project still-recipe-75029973, branch br-misty-pond-ba8kkw7s, PostgreSQL18, aws-eu-central-1. Compute0.25CU fixed; conservative project quotas80CU-hours,4GB transfer,500MB logical data; history6hours. Endpoint API reported idle timeout0 despite documented Free policy; idle auto-suspension is not claimed as measured. Free-plan/quota exhaustion may interrupt availability.
- Empty database verified before authorized initialization:47 Alembic-generated statements applied in one transaction;18 tables/head8022c27c58ae verified. Runtime devtreck_app has no superuser/createdb/createrole/schema-create privileges. Exact production origin and encrypted environment values configured. Startup never migrates.
- Initial managed PostgreSQL readiness failed due to CA trust. Fixed explicit certifi trust bundle and10-second connection timeout; preserved verify-full and channel_binding=require. Direct TLS SELECT and final hosted readiness succeeded; all73 API regression tests reran successfully.
- From apps/web: `npx playwright test --config playwright.hosted.config.ts`: **1 passed in23.3seconds** (journey22.4seconds). Real hosted signup/login, secure cookies, tasks/habit/checklist, focus pause/reload/stop,15XP, anonymous401, CSRF/Origin403, headers, docs404, desktop/mobile screenshots, axe0violations and authenticated account deletion. Database read confirmed users0 and migration head after cleanup. Mobile screenshot visually inspected.
- Free snapshot snap-broad-dew-bazcsfaj, phase10-verified-baseline, created after cleanup. This is an empty-schema baseline, not continuous protection of future user data. No paid or daily backup scheduler activated.

Hosted test/config and Vercel deployment files are included in source. Hosted tests are opt-in and excluded from uploaded app files. CLI65.12.1 uploaded clean worktree source; current deployment API includes commit24e99d9. Existing password-minimum edits remain untouched in the primary worktree; deployment uses checked-in12-character policy. Details/operations: docs/deployment/FREE-HOSTING.md and RUNBOOK.md.

## Limitations, Git and handover

Free-tier caps/cold starts can interrupt availability. Hobby is personal/non-commercial only. Serverless process limits are per-instance, not a distributed abuse-control guarantee; app pools can multiply under concurrency. Local Caddy request/log/forwarding/shutdown controls are not claimed as Vercel controls. No public load test, Firefox/Safari matrix, full provider-log audit or hosted CI run is claimed. Proposed RPO24hours/RTO60minutes and daily/weekly backup retention remain targets; automated off-provider backup scheduling is not configured. Baseline snapshot plus6-hour provider history is the actual current recovery coverage.

Optional notifications/password recovery/custom recurrence remain deferred as in prior phases. Historical missing denominators remain unavailable. No unfinished provider controls were enabled. All test data is synthetic; hosted test account was deleted. Local development data was not migrated to the cloud: sign up separately online.

Branch codex/phase-10 contains focused commits3d0e052 (hardening/packaging),6b2116b (tests),659de16 (initial local handover),d5cf9e0 (Vercel deployment),24e99d9 (TLS trust fix), followed by hosted verification/final handover. Clean deployment worktree uses codex/deploy-personal-free. No push, PR, main/develop merge, history rewrite, remote change or visibility change. Three pre-existing password-policy files remain unstaged and excluded. Local app remains http://127.0.0.1:3000 and local production proof https://localhost:8443.

Usable online: account/profile/settings, tasks/categories/search/filter/history, daily habits and streaks, plans/priorities, checklists, persistent focus sessions, XP/levels/achievements and progress insights. User action: open https://devtreck.vercel.app and create a personal account. Phase10 ends here with the above operational limitations documented.
