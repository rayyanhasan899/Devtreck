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
