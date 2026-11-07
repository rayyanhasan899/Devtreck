# Devtreck release runbook

Live personal deployment: https://devtreck.vercel.app, with FastAPI at https://devtreck-api.vercel.app and Neon Free PostgreSQL. Both Vercel projects use the verified Hobby team raan-899. No Render resource was created. Strict $0 and personal/non-commercial use apply; see [hosting decision](FREE-HOSTING.md). Local production verification remains separately reproducible.

## Local production stack

Prerequisites: Docker Compose v2+ compatible CLI, existing API venv dependencies for helper scripts, installed web test dependencies/Chromium. From repository root:

```powershell
python scripts/release_env.py
docker compose --env-file deploy/.env.release -f deploy/compose.release.yaml build
docker compose --env-file deploy/.env.release -f deploy/compose.release.yaml up -d --wait
apps/api/.venv/Scripts/python scripts/recovery_drill.py
apps/api/.venv/Scripts/python scripts/release_checks.py
```

The credential generator creates only ignored `deploy/.env.release` using exclusive creation; reruns intentionally refuse overwrite. Keep the file private and preserve it with the release database volume. Never print `docker compose config`, process environments, database URLs, or secrets into logs/chat. On Linux use the installed venv's Python instead of the Windows executable path.

From apps/web run `npx playwright test --config playwright.release.config.ts`. This targets only `https://localhost:8443` and synthetic test accounts, using a dedicated browser context that accepts this local private CA. It deletes its own account on success; failed runs may leave synthetic accounts. It is not an external production test runner. Normal browser journeys continue to use the generated disposable database runner.

Open https://localhost:8443 for the isolated release stack. The browser will require trusting its local CA. `release_checks.py` exports only the **public** CA certificate to ignored `.release-results/caddy-root.crt` and verifies HTTPS against it. Import this certificate into your browser/user trust store only if you choose to trust this local instance; never distribute its private keys or disable TLS verification globally. Ordinary local development remains http://127.0.0.1:3000 with its existing database and accounts; release-stack accounts are separate.

Architecture: Caddy HTTPS proxy routes `/api/*`, `/health`, `/ready` to FastAPI and other paths to Next standalone. Only proxy port8443 is bound, on loopback. DB/API/web ports are private to the Compose network. API/web run non-root with read-only roots, temporary writable caches, dropped capabilities, no-new-privileges, init and30-second shutdown grace. The migration one-shot uses the owner role; the API role cannot create databases/roles/schema objects. Production application startup never migrates. The Compose recipe is **local-only** and its initial synthetic migration is authorized; do not point it at a valuable/external database.

Images pin Python3.14.7, Node24.15.0, PostgreSQL18.6 and Caddy2.11.9 by immutable digest. Rebuild/test intentionally when updating digests. API installs the existing complete pinned Python lock (including development tools); it does not expose a shell/DB port publicly. Web installs npm lock and ships traced standalone output/public/static, not source dependencies. `STANDALONE_BUILD=1` is container-only so ordinary Windows `npm run build`/`npm start` keep working. API_ORIGIN is fixed at build and runtime to private `http://api:8000`; changing it requires rebuilding web.

Health: `/health` means process liveness; `/ready` verifies DB connectivity. Compose waits for DB, explicit migration success, API and web health. The proxy has its own health check. Restart policies recover exited long-running containers; unhealthy-but-running processes need operator investigation/restart. API upstream connection reuse is disabled to avoid partial-body/idle connection reuse after size rejection or upstream restarts. Container logs use no access/query/body logging; Caddy runtime errors remove the complete request object, including query and headers. API unexpected failures log only exception type and request ID. Password hashing/verification permits at most two concurrent memory-heavy operations per API process; overload returns safe503 and can be retried. Database transactions roll back on failed requests.

Stop/restart without deleting storage:

```powershell
docker compose --env-file deploy/.env.release -f deploy/compose.release.yaml stop
docker compose --env-file deploy/.env.release -f deploy/compose.release.yaml up -d --wait
```

`release_checks.py` deliberately stops/restarts **only this local release API**, verifies a502 outage, then recovery and sanitized failure logs. Do not run that drill against a live external deployment. Do not use `down -v`, `volume rm`, reset, or downgrade on valuable data.

## Recovery and backups

Proposed personal-use objectives: RPO<=24hours with a successful daily external backup; RTO<=60minutes after credentials/hosting access is available. These are operational targets, not measured hosted guarantees. The local synthetic drill proved0 lost records and 3.77seconds restore+verification for a tiny dataset, not large-database throughput or cloud recovery. Neon Free's limited instant-restore history is supplementary, not a daily-backup replacement.

`scripts/recovery_drill.py` creates only generated `devtreck_drill_<uuid>` and `devtreck_restore_<uuid>` databases inside the isolated release DB container. It upgrades cleanly through phase8 then incrementally to head, checks metadata, seeds account/session/category/task/type-change/daily/checklist/plan/focus/reward data, dumps custom-format with `pg_dump`, restores with `pg_restore --exit-on-error`, and compares row counts and SHA256 of **every full row** across all18 tables including migration state. It checks restored metadata, removes only its own temporary dump and generated databases, and writes non-secret counts/timing to ignored recovery.json.

Before a real migration, obtain explicit approval, make a verified custom-format backup using a PostgreSQL client matching the server major version, and record the code/image commit and `alembic current`. Supply credentials via protected environment/pgpass or provider secret flow, never command-line URLs. Example commands in a secure operator session:

```text
pg_dump --format=custom --no-owner --no-acl --file=<private-backup-path>
pg_restore --exit-on-error --no-owner --no-acl --dbname=<new-empty-recovery-db> <private-backup-path>
```

PGHOST/PGPORT/PGUSER/PGDATABASE and TLS credentials must already target the intended database. Use a **new empty recovery DB**, never `--clean` on live data. Restore table owners/grants with reviewed privileged access; verify Alembic head, checksums/counts and private account/task/focus/XP journeys before cutover. Rotate session/database credentials if a backup or environment may have leaked.

Retention proposal: encrypted daily backups retained7days plus weekly backups4weeks, on private user-controlled storage distinct from the server; record/check checksums, restrict access, test monthly. No external scheduler/storage service has been provisioned and no automated external backup currently runs. User must configure an approved no-cost schedule/location after account access; do not substitute a paid backup feature. Backups contain private account hashes/session hashes/task history; never commit/upload them as CI artifacts. Local test reports/screenshots contain only synthetic data.

## Migration and rollback gates

Every code release: lint/type/tests, clean+incremental migration tests, build, recovery drill, production journey, backup confirmation, and schema-compatible image review. Apply `alembic upgrade head` only from a secure operator environment with the **direct** Neon migration-role URL and explicit approval. Never put migrations into API startup. Use a secure operator session with the migration role; the runtime role is deliberately restricted. No automatic migration workflow is active.

Prefer an additive forward-fix. Roll back to the previously verified image only if compatible with the current schema; a code rollback does not undo schema changes. Keep the application in maintenance/read-only mode when schema/data safety is uncertain. A destructive downgrade or database replacement needs a reviewed restoration/cutover plan and explicit approval. The fresh, empty hosted database received the authorized additive schema initialization. No valuable-data downgrade or reset occurred.

## Live resources, deployment and checks

- Team: raan-899, Hobby; frontend project prj_yAGsHD8axZXi6KeTM3CTCuL2uO65; backend prj_6wc14N3wpljtjde7YfyUM9lpWP84.
- Neon: still-recipe-75029973, branch br-misty-pond-ba8kkw7s, database devtreck, PostgreSQL18, Frankfurt. Schema head8022c27c58ae. Owner devtreck_owner is for migrations; restricted devtreck_app is for runtime.
- Frontend production deployment dpl_5euCUktAT1qTAsPd8sqTGocAytwP; backend dpl_ATJvauDPXhnTuC8NkK8syHRtaqBx. Public aliases above are usable; generated preview deployment URLs may require Vercel authentication.
- Source was uploaded from clean worktree D:/RAYYAN/Projects/Devtreck-release on codex/deploy-personal-free, excluding three unrelated local password-policy edits. Hosted password minimum is the checked-in12characters. No Git remote integration/push or automatic deployment was enabled.

Vercel CLI65.12.1 is authenticated through its official device flow. To deploy a reviewed revision, use a clean worktree, run the API and web checks, and deploy each linked app directory with `npm exec --yes --package=vercel@65.12.1 -- vercel deploy --prod --yes --scope raan-899`. Deploy API first, verify /ready, then web. Confirm both projects remain Hobby and no upgrade/add-on prompt is accepted. Keep app/main.py FastAPI detection, apps/api/vercel.json fra1/60seconds, and frontend Node24. Do not set STANDALONE_BUILD for Vercel.

Production API environment: APP_ENV=production, APP_DEBUG=false, ALLOWED_ORIGINS=["https://devtreck.vercel.app"], encrypted DATABASE_URL for the restricted direct TLS role. Frontend environment: server-only API_ORIGIN=https://devtreck-api.vercel.app. No NEXT_PUBLIC secret. Secret values are in provider encrypted environment settings; the local deployment helper configuration is Windows-DPAPI encrypted outside Git under the current user's LocalAppData/DevtreckTools. Never print, commit or share these files or decrypted contents. CLI credentials use their normal user storage.

From apps/web, `npx playwright test --config playwright.hosted.config.ts` creates and deletes its own synthetic account on the actual public site, with normal certificate verification. It exercises writes, so run deliberately, not on every CI push. A failure can leave that synthetic account; remove it using its own authenticated account-deletion flow, never by deleting unrelated database rows. Screenshots/traces remain ignored and contain synthetic data. Verify backend /ready200 and frontend /login200 after each release.

Hosted limits differ from Docker: Vercel owns ingress, lifecycle and request limits; local Caddy's128KB cap,30-second graceful shutdown, proxy log filtering and forwarding drill are local evidence only. Application security tests and live cookie/CSRF/Origin/auth tests pass, but no distributed rate-limit guarantee, full provider-log redaction audit or high-concurrency benchmark is claimed. In-process limits reset across serverless instances. Quota exhaustion/cold starts can show the existing retry UI.

## Backup status and remaining operations

Free baseline snapshot: snap-broad-dew-bazcsfaj (phase10-verified-baseline), created2026-11-07 after hosted test cleanup. Neon project restore history21600seconds. The baseline protects initial schema only, not future user changes. No paid backup schedule/storage was activated. The daily/weekly encrypted off-provider backup policy above remains a proposal; no scheduled external backup currently runs and24-hour RPO is not achieved by this snapshot alone. Configure a deliberate private no-cost backup destination/schedule before relying on those recovery objectives. The synthetic local18-table restore drill passed with zero loss.

The app is usable now: open the frontend URL and sign up. No further credentials are needed to use it. Preserve personal-use eligibility; reassess providers before commercial use. Check Vercel/Neon usage periodically and before widening access. No remote push, PR, main merge, custom domain or paid resources were created.
