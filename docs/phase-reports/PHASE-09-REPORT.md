# Phase 09 report — rewards and trustworthy insights

Date: 2026-11-07. Exit result: **PASS WITH KNOWN LIMITATIONS**. Phase boundary respected; phase 10 release/hosting is not implemented. No manual action is required to use the local app.

## Objective and delivered behavior

Implemented ACH-01–07, INS-01–07, UI-01/06/09–12 and relevant requirements §§16.4/17: server-owned source-based XP, level progress, four unique badges with reason/date, automatic valid-history backfill, atomic task/focus rewards, stable eligible occurrence snapshots, local-date insights, focus totals/session counts, streak summaries, daily actual-data table/bars and current-category breakdown. Protected Progress navigation/page shows loading/empty/error/retry, transparent rules, coverage and insufficient-history explanations.

One-time first completion earns10 XP; unique habit day5; completed focus session with >=1500 active seconds5, at most4 focus rewards per local end date. Level1+floor(XP/100). Five server environment overrides are bounded and documented in .env.example; source amounts and policy fingerprints remain immutable. Badge criteria: first occurrence, seven consecutive habit dates within an epoch, 25 distinct task IDs and 300 minutes of closed active focus intervals. No checklist completion grant or automatic parent completion.

Completion and reward changes share a transaction. Existing owner locks plus unique source constraints prevent retries/concurrent grants. Zero-value cap-skip entries freeze denied sources. Archived task/associated focus history is excluded from Progress; earned minimal non-content XP/badges remain. Account deletion cascades all phase-9 records.

## Changed files and design

Created API domain/rewards.py, persistence/progress.py, services/progress.py, presentation/progress.py, migration8022c27c58ae, tests/test_progress.py; web features/progress/progress.tsx, app/app/progress/page.tsx and tests/progress.spec.ts. Modified API settings/composition/models, task/productivity services and route dependencies; web global styles and AppShell navigation. No files deleted. Existing account_schemas.py/auth-form.tsx/settings.tsx password-policy edits are unrelated and deliberately excluded from phase commits.

Added docs/api/progress.md and ADR-0009, updated README, assumptions A-09/A-46–50, API productivity, database foundation, setup/preconditions, testing guide, traceability and .env.example. See the reward/insight contract for exact formulas, provenance, backfill timezone and category/deletion semantics. Requirements and blueprint were inspected alongside master plan, assumptions and relevant phase-8 evidence. The attached prompt was executed within the user's explicit phase request; examples were interpreted through source requirements.

Eligible denominator = observed due one-time occurrences plus active daily dates. Save snapshots before schedule changes and fill unchanged schedules across idle dates; freeze first observed one-time due occurrence. Missing historical schedules are not fabricated: rate null if zero denominator or incomplete current-zone date coverage. Initial weekly rates may therefore be unavailable. Completion activity and XP can still backfill from trustworthy records. These documented interpretations are implemented under the submitted prompt; no separate approval is pending.

## Verification evidence

Actual working directory `D:\RAYYAN\Projects\Devtreck\apps\api`:

- `.venv/Scripts/python -m pytest`: **68 passed in33.86s**, including nine phase-9 tests and all earlier account/persistence/task/streak/productivity tests. Real isolated PostgreSQL databases, upgrade/base/head round trips and metadata comparison; no skipped acceptance tests.
- `.venv/Scripts/python -m ruff check .`: all checks passed. `ruff format --check .`:53 files already formatted. `mypy app`: no issues in45 source files.
- `alembic upgrade head`, `alembic check`, `alembic current`: local additive migration applied, no new upgrade operations detected, head8022c27c58ae. No local valuable-data downgrade/reset.
- `.venv/Scripts/python scripts/browser_checks.py`: **7 passed (1.1m)**, full account/task/productivity/Progress Chromium suite. Runner invokes Playwright tests against generated disposable database and temporary services, then cleans only those resources. Progress-specific rerun also passed. Axe reports zero violations on final Progress scan; widths360/768/1440 have no document overflow. Final ignored progress-desktop.png/progress-mobile.png visually inspected.

Actual working directory `D:\RAYYAN\Projects\Devtreck\apps\web`: `npm run lint`, `npm run typecheck`, `npm run build` passed. Final production build includes dynamic `/app/progress`. Prettier applied to changed frontend files using npm exec; no dependency/lock changes.

Explicit records verify one-time/daily concurrent retries, immutable configurable awards, transaction rollback on reward failure, backfill/repeat badge uniqueness, all four milestones, focus min-duration/break/stopped exclusions, four-per-day cap and next day, concurrent cap backfill, archive/account deletion, owner separation, anonymous401/arbitrary XP POST405, zero/unknown denominators, exact50% and12.5% rates, idle daily snapshots/type conversion, local-midnight/DST focus split and original qualifying dates.

Local runtime refreshed: API8002 and production web3000 running. HTTP smoke: API readiness200, anonymous direct/proxied Progress401, web login200, protected `/app/progress`307 to login. Existing development accounts retained. No synthetic records were added to development for testing.

Versions inspected: Python3.14.7, Node24.15.0, npm11.12.1, Next16.4.5, React19.3.0, SQLAlchemy2.1.8; existing pinned API/frontend locks retained. SQLAlchemy official2.1 PostgreSQL ON CONFLICT documentation checked; installed Next server/client guide read before UI work. No new package selection required.

## Failures and resolutions

Initial lint/type checks caught default-constructor lint and local variable typing; corrected before acceptance. A fixture accessed an expired detached ORM object's ID; captured it while attached. A newly added concurrency test initially missed its ProgressService import; corrected and reran the full68-test suite. Browser checks caught a selector matching Next's route announcer, then a real missing main/skip landmark, then a narrow-grid overflow. Scoped the assertion, added semantic main/skip target and bounded responsive grids; final full browser suite passes. Screenshot review prompted smaller mobile summary numerals and consistent themed progress styling. All identified acceptance failures resolved.

## Limits, security and manual actions

Historical denominator gaps intentionally remain unavailable, rather than inventing rates. Historical focus rewards use the profile zone at first evaluation because earlier sessions had no zone field; stored reward dates/amounts never relabel. Category grouping is current assignment; streak summary is current daily tasks. Existing raw `/focus/summary` retains its prior archive-inclusive work totals, while Progress applies the documented exclusion. Badge focus milestones materialize closed intervals; live analytics also include current capped active work. Derivation scans owner history; exceptionally large histories may need measured incremental aggregation. No external analytics collection or client-authoritative reward fields.

Local Windows Chromium and production HTTP/build checked; no hosted CI, Firefox/Safari matrix, external deployment or production backup drill claimed. Local app is usable now at http://127.0.0.1:3000/app/progress after sign-in. No manual setup remains for this checkout. Fresh clones follow README, environment examples and additive Alembic upgrade; phase10 external hosting still needs a target/domain/budget.

## Git state

Branch `codex/phase-09`. `cef5898` implements rewards/insights; `889fa1a` adds API/browser coverage; this report and related contract/setup docs are included in the final documentation commit. Existing origin preserved. No push, PR, merge, history rewrite or main/develop update performed. Three previously present password-policy changes remain unstaged in account_schemas.py, auth-form.tsx and settings.tsx. Tests were run against the shared working tree containing those preserved edits. Phase-9 work is locally committed in focused milestones.
