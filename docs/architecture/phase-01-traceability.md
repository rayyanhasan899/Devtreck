# Foundation requirement contributions

| Requirement | Evidence | Check |
|---|---|---|
| NFR-14,16 | API composition/config/presentation; strict TypeScript; Ruff/mypy | lint/types |
| NFR-17 | README, env example, dependency locks, ADR | install/run |
| NFR-18 | Config and liveness tests; later account/task/streak tests remain pending | pytest |
| NFR-19 | Semantic responsive landing with system themes | build/HTTP smoke; full browser QA later |
| NFR-20 | Ignored local env; validated settings; required database password | negative tests/Compose startup |
| Blueprint 17,29,32,42 | Config/docs/focused commits/CI | local checks; hosted CI separately |

These are contributions, not claims that all future feature requirements are satisfied.

## Phase 9 contributions

| Requirements | Code | Evidence |
|---|---|---|
| ACH-01–07, NFR-07/15 | domain/rewards, persistence/progress, services/progress, task/productivity transaction hooks | test_progress: source retries/concurrency, toggle, rollback, cap, eligibility, configurable immutable ledger, all badges/backfill |
| INS-01–07, §16.4, §17 | occurrence/coverage models, ProgressService.report, GET /api/progress | exact 50%/12.5% fixtures, zero/missing denominators, idle snapshots, zone/DST bounds, archive filtering, owner scope |
| UI-01/06/09–12 | protected /app/progress, semantic tables, level progress, badge dates, retry and navigation | progress.spec.ts: empty/populated/reload/error, axe/landmarks, 360/768/1440, deletion with XP retained |
| SEC-01/02/03/14 | existing authenticated owner locks; cascades and no XP write endpoint | anonymous401, second-owner empty report, arbitrary XP POST405, account cascades |

API references above are relative to apps/api/app; browser references to apps/web. This updates feature coverage without claiming external deployment, browser matrices or hosted CI.

## Phase 10 final audit contributions

| Requirements | Implementation and evidence |
|---|---|
| SEC-01–14, §§15–17 | docs/testing/release-readiness.md private-route matrix maps all groups to existing owner/CSRF/Origin/cascade tests; new test_release verifies anonymous routes, production cookies/docs, safe500 logs, auth resource overload/recovery, batched queries and index capability |
| NFR-01–08,10–16,18,20–21 | existing account/task/streak/productivity/progress tests and seven browser journeys; batch500 occurrence writes, strict transaction/source invariants, safe errors, centralized client and typed build |
| NFR-09/17; blueprint42–43 | digest-pinned Docker packaging, restricted role/explicit migration, local Caddy HTTPS, full-row checksum restore drill, runbook/RPO/RTO/retention targets, CI release job and production HTTPS journey |
| NFR-19 | local Chromium desktop/mobile widths and axe; no unrun Firefox/Safari or hosted matrix claimed |
| External release / budget | docs/deployment/FREE-HOSTING.md: final personal-only Vercel Next+FastAPI and Neon $0 decision; actual Hobby/Free plans, restricted TLS role and encrypted secrets; hosted-tests/hosted.spec.ts passed signup/tasks/focus/XP/cookies/CSRF/account deletion; no Render resource |

Full code/test paths and actual outcomes are recorded in PHASE-10-REPORT.md. No automatic production migration, external backup scheduler, paid resource or main merge is implied.
