# Phase 05 report — Daily completion and streak engine

2026-11-07, Asia/Karachi. Status: **PASS WITH KNOWN LIMITATIONS**.

## Scope and implemented functionality

Daily tasks now accept completion through POST complete and PATCH status completed. Server clock and profile IANA timezone determine immutable completion day, UTC-aware timestamp and zone provenance. First completion is one, consecutive local days increment, duplicate/concurrent same-day requests count once, missed yesterday resets current on read and lifetime best remains. Daily reopen cannot erase credit; global status remains pending while nested today_completed describes occurrence state.

Responses expose current/best, today state, last recorded day, total daily completions, current local day and timezone. Daily and All retain completed-today habits; Today excludes them until next local day. Completed view/status includes daily tasks credited today. One-time tasks retain separate first-completion behavior and streak:null; direct streak endpoints for one-time tasks reject with 409.

New all-epoch daily-history endpoint is bounded/owner-scoped and survives type conversions. New authenticated reconcile endpoint repairs stored counters from immutable facts; public reads calculate fresh counters even when caches age at midnight. No cron/midnight worker required.

## Requirements and architecture

STR-01–11, TSK-06/18–19/21/23–24/27, NFR-07–08/15/21 and requirements 7/16.3: domain/streaks.py contains framework-free clock/calendar/rule logic; service orchestrates owner-before-task locks and transactions; repository enforces owner filters, composite FK and unique task/local-day constraint with atomic conflict-safe insert. New fact and cached counters commit together. No client timestamp/day/epoch/counter accepted as authoritative. Clock injection is a backend dependency/test override only, never a public parameter.

Daily epochs restart current at zero on reactivation; old facts/one-time history remain unchanged. Lifetime best is highest run within any epoch, never bridged across epochs. Task/day uniqueness spans epochs, preventing same-day type-toggle credit. Existing daily tasks receive a fresh epoch and zero credit in migration.

Profile timezone updates and completions use the same user lock. Completion reads refreshed zone only after locking and then samples server time. Historical labels never change. Future-labeled records after westward travel remain visible/best-eligible but are excluded from current-run computation until applicable. The explicit policy and UI notice requirement are in docs/api/streaks.md; browser settings UI is still phase 6.

## Files, decisions and assumptions

Added app/domain/streaks.py, revision 686071c1a9b8 and tests/test_streaks.py. Extended models/repository/service/schema/routes and task regression tests. Added tzdata as explicit direct dependency at existing locked 2026.6 version; no package upgrades or new installs needed. Added streak API guide and ADR-0005; updated task guide, README and assumptions. No files deleted.

ADR-0005 records immutable daily facts, epochs, lock order, timezone behavior, reconciliation and batched summaries. A-02/A-10 progressed; A-28–31 record cross-epoch day uniqueness, westward-zone behavior, daily occurrence state and separate histories. Details remain explicit recommendations implemented under phase authorization, not invented baseline requirements.

## Verification and actual evidence

Existing Python 3.14.7, SQLAlchemy 2.1.8, Alembic 1.20.1, psycopg 3.3.8, PostgreSQL 18.6, pytest 9.2.0, Ruff 0.17.4, mypy 2.4.1 and Node 24 retained. Official Python zoneinfo documentation checked; pinned tzdata already installed for Windows.

From apps/api:

- python -m ruff check .: passed.
- python -m ruff format --check .: 39 files passed.
- python -m mypy app: 34 source files passed.
- python -m pip check: no broken requirements.
- python -m pytest: **52 passed**, no skips/warnings; 21 streak-specific cases and 31 earlier regression tests.
- Targeted streak run: 21 passed, including migration backfill.
- Disposable migration base/head round-trip and schema agreement checks passed as part of suite. Separate prior-phase-to-head backfill test seeds existing daily task, upgrades and verifies epoch with current/best zero and no invented completion.
- Local development alembic upgrade head/check/current passed at 686071c1a9b8 with no schema drift. No valuable data reset.

Evidence covers zero/first/consecutive/gap/reset/best, duplicate days, server timestamp provenance, naive-clock rejection, Karachi midnight, positive UTC offsets, New York DST spring gap/fall repeated hour, 23/25-hour day midnight edges, today-pending yesterday run, live view rollover, reopen preservation, corruption reconciliation, bounded history and unauthorized ID rejection, timezone-edit immutability, recurrence epoch conversion without duplicate credit, concurrent completion in independent transactions, direct-DB duplicate rejection and profile-edit lock serialization. Archive hides facts; account deletion cascades them. Earlier one-time completion and ownership/security tests still pass.

From apps/web: npm run lint/typecheck/build all passed; no UI source changes. Refreshed API on 127.0.0.1:8002 returned readiness 200; live OpenAPI includes streak and daily-history routes. git diff --check verified before commits.

## Failures and resolutions

Ruff found imports/unused fixture variables; fixed before final checks. Existing phase-4 daily-completion rejection assertions were updated to the now-supported behavior while preserving one-time history assertions. Long documentation shell write was rejected by automatic review; completed documentation with explicit file edits. Existing mixed assumptions-file encoding/line endings prevented one edit; normalized to UTF-8/newlines while retaining prior contents, then added phase updates. No unresolved application/test failures.

## Security, data integrity and limits

No client clock or final counters trusted; immutable history and uniqueness guard retries/concurrent writes. Both profile and task locks use consistent user-before-task ordering. Cached values never determine authoritative read responses. New daily history rows include owner FK and account cascade. No secret values printed/committed and ignored local config unchanged. Tests operate solely on guarded random disposable databases, including the explicit backfill downgrade/upgrade. Local development received the additive verified migration only; no production operation.

Known limitations: no browser habit/streak screens until phase 7, settings UI phase 6, hosted CI/Linux execution not run here. List pages batch daily histories in one query but long-history performance still requires measurement. Stored cache can age after midnight until mutation/reconcile; public display is fresh. Future-labeled historical dates after timezone travel follow the documented rule; no hidden rolling-24-hour anti-travel policy. No recovery/freeze, custom recurrence, notifications or XP rewards implemented. Optional features remain deferred.

## Git and handover

Branch codex/phase-05 continues verified history. b4d2a37 implements daily facts/engine/contracts/migration; 14d5815 adds boundary/concurrency/backfill tests; final docs commit records evidence. Main/private origin unchanged; no push/PR/merge or history rewrite.

No manual setup action required. Updated API left running on port 8002; older 8000/8001 processes may serve old code. **Usable now:** account/profile APIs, task/category CRUD/search/views, one-time completion/history, daily completion and current/best streaks, all-epoch daily history and cache reconciliation. API docs: http://127.0.0.1:8002/docs. Website remains welcome page; browser product workflows arrive in later UI phases. Stop here and await phase 6 prompt.
