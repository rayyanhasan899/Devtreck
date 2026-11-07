# Devtreck release runbook

Local release readiness is verified separately from external deployment. External deployment is currently **BLOCKED** on provider account/billing verification, secure access, and explicit production migration approval. The latest user decision is personal/non-commercial use only, Vercel Hobby + Render Free (FastAPI only) + Neon Free, provider subdomains and a strict $0/month target. No paid upgrade, trial requiring payment, custom domain, or billable resource is authorized. See [hosting decision](FREE-HOSTING.md).

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

Every code release: lint/type/tests, clean+incremental migration tests, build, recovery drill, production journey, backup confirmation, and schema-compatible image review. Apply `alembic upgrade head` only from a secure operator environment with the **direct** Neon migration-role URL and explicit approval. Render Free lacks one-off jobs/shell/pre-deploy support; never sneak migrations into API startup. Use a controlled local/CI manual workflow if one is later authorized; no production migration workflow is active here.

Prefer an additive forward-fix. Roll back to the previously verified image only if compatible with the current schema; a code rollback does not undo schema changes. Keep the application in maintenance/read-only mode when schema/data safety is uncertain. A destructive downgrade or database replacement needs a reviewed restoration/cutover plan and explicit approval. No production downgrade, dump, migration or reset occurred in phase10.

## External preflight and exact pending actions

1. All three integrations are now confirmed installed. Neon account reads succeed and show Free with no projects. Render workspace calls currently fail with an unknown-operation integration error, and Vercel account tools are not exposed in this chat; the browser fallback could not initialize. Refresh/reconnect the existing Vercel/Render access through the official flows, or continue account verification in a session where they work; do not reinstall Neon or post credentials. Confirm each account is on a genuine free plan, with no trial/add-ons and no automatic paid usage. If card verification/payment is required or an existing account can incur charges that cannot be disabled, stop. No payment details in chat.
2. Confirm personal/non-commercial use remains accurate. Retain the private personal GitHub repo and chosen branch; do not publish it. Decide and commit the three pre-existing password-policy edits before building a live release so source policy and images match.
3. In Neon Free choose one project in a region close to Render, preferably PostgreSQL18 when offered. Obtain separate owner/migration and restricted app-role URLs securely; require TLS with certificate/hostname validation. Existing psycopg/libpq18 supports `sslmode=verify-full&sslrootcert=system&channel_binding=require`; verify the real connection before release. Default app pool is5+5 connections per process with pre-ping and a3-second connection timeout; use one API process and verify actual Neon connection/compute limits. Use direct connections initially; do not substitute pooled URLs without checking startup options/timezone/prepared-statement behavior.
4. Obtain migration approval and apply reviewed head to the empty project; set restricted default/existing table privileges as in init-app-role.sh (adapt owner role/database names, never reuse local passwords). Verify role restrictions and readiness. Do not point a CREATEDB test fixture at Neon/live data.
5. Import reviewed `render.yaml` for **one Free Docker web service**, no Render Postgres, disk, worker or paid build machine. Configure secrets only in provider settings: APP_ENV=production, APP_DEBUG=false, DATABASE_URL=app-role Neon URL, exact ALLOWED_ORIGINS containing the final Vercel HTTPS origin. Automatic deployments are disabled. The Render command disables trusting forwarded headers because the service is internet-addressable; address throttling is conservatively shared at Render's peer unless a verified trusted-header boundary is designed. Per-email limits remain. Do not copy the local private-network `forwarded-allow-ips=*` command to a public host.
6. Import apps/web in Vercel **Hobby**, Node24, Next framework, npm ci/build, no standalone flag. Set server-only API_ORIGIN to the actual Render HTTPS origin **at build and runtime**. Keep browser calls relative `/api` so host-only Secure/SameSite cookies remain same-origin through Next rewrites; do not enable wildcard CORS or cross-site cookie exceptions. Disable unsolicited integrations/analytics and preview deployments with real data. Do not expose DATABASE_URL or secrets as NEXT_PUBLIC_*.
7. Verify free-account billing safeguards/usage emails, cold-start/SSR timeout behavior, proxied cookies, CSRF/origin rejection, per-user ownership, production headers, log redaction and health/failure recovery **on the actual providers** before calling it deployed. Render sleep can take about a minute and can exceed frontend rendering/proxy timeouts; the UI may show its retry state. Do not add keepalive traffic to defeat free-tier sleep or promise always-on service.
8. Verify the approved encrypted backup schedule, usage headroom and small private synthetic end-to-end account journey on the real URLs; delete the test account afterward. Only then record a live release URL and deployment evidence. None exists yet.

Before pushing this private repository's CI workflows, also verify GitHub Actions included minutes and a zero-spend budget/overage block. No hosted CI was triggered here, and free quotas on one provider do not guarantee free usage on another.
