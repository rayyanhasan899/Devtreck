# Rewards and progress

GET `/api/progress` requires the signed-in session and returns only that user's derived report. No user ID, XP amount or achievement write is accepted. No public leaderboard. The endpoint settles an elapsed focus session, validates/backfills rewards and snapshots eligible dates before returning typed JSON with `Cache-Control: no-store`. Refresh safely retries these derived writes. Existing mutations retain Origin and CSRF protection.

## Reward contract

Default environment configuration in `apps/api/.env`:

| Variable | Default | Meaning |
|---|---:|---|
| REWARD_TASK_XP | 10 | Lifetime first one-time completion |
| REWARD_DAILY_XP | 5 | Unique task/qualifying date |
| REWARD_FOCUS_XP | 5 | Completed eligible focus session |
| REWARD_FOCUS_MIN_SECONDS | 1500 | Minimum active focus seconds |
| REWARD_FOCUS_DAILY_CAP | 4 | Rewarded focus sessions per local completion date |

Values are server-validated bounded integers. Level is fixed at `1 + floor(total XP / 100)`; next threshold is `(floor(total XP / 100)+1)*100`. No new dependencies. Rewards encourage meaningful work, not competition; duplicate task creation is not semantically deduplicated. Personal XP is not an anti-fraud or leaderboard score.

Completion and reward writes share one transaction. Owner locks serialize concurrent retries/cap checks; unique `(user_id, source_kind, source_id)` provides a database backstop. Reopen does not remove source facts, so toggles do not earn twice. Checklist items never produce task XP. Daily sources retain their original qualifying date across timezone/epoch changes. Focus requires completed status, kind focus and sufficient active seconds; stopped, short and break sessions receive no focus XP. Pauses are excluded by the existing interval engine. A fifth eligible session gets a minimal zero-XP `focus_skip` record, preventing cap-denied history from gaining XP after timezone changes.

Earlier valid facts are backfilled on progress reads and subsequent product writes, in deterministic focus end-time/ID order. Each ledger entry retains source ID/type, amount, event/award instants, frozen reward date and rule fingerprint. It contains no task content and has no task deletion FK. Historical focus dates use the account timezone at first reward evaluation because pre-phase-9 sessions did not capture a timezone. Awarded amounts/dates are never rewritten after configuration or timezone changes. Already processed sources, including cap skips, are not replayed. Focus sessions that were ineligible under earlier configuration can become eligible under a later lower threshold; awarded sources remain unchanged.

Badges are unique per user/key: first task occurrence; seven consecutive dates within one daily epoch; 25 distinct completed task IDs (a habit counts once); 300 minutes of recorded closed focus intervals, including stopped work but excluding breaks/pauses. Badges show reason and first verification date, including historical backfill; they are never revoked. An active interval contributes to live analytics, and to the milestone once closed/materialized.

## Insight contract

Periods are today and today minus six through today, inclusive in the current IANA zone. Daily completion activity uses immutable qualifying date; one-time activity uses the event timestamp converted to current zone. Activity counts lifetime first one-time completions plus qualified daily occurrences, never checklist items. Thus completing overdue work can increase activity without increasing today's eligible numerator.

Completion rate = completed eligible occurrences / eligible occurrences in that displayed period. Daily occurrences are materialized for active dates. A one-time occurrence uses its due date (or local timed-deadline date), frozen when first observed due; it remains eligible after reschedule/reopen/type edits. A completed one-time occurrence counts in its due period when its immutable completion timestamp is before that period's end. Undated one-time tasks have activity/XP but no rate denominator. An occurrence is counted once. All rates require a positive denominator and complete date coverage in the current timezone; otherwise JSON null/UI Unavailable, with covered/expected dates shown.

Tracking starts at the first phase-9 product write or Progress read. There is no invented denominator for earlier schedules. On subsequent reads/writes, unchanged schedules fill idle dates since the last coverage date; snapshots are taken before schedule mutations/deletion and after saves. New daily activations cannot populate dates before activation. A timezone change conservatively leaves earlier-zone coverage unavailable; it does not relabel historical snapshots. Coverage is not a claim of a complete pre-phase-9 history. Backdated deadlines can introduce a first observed occurrence on the supplied past due date.

Focus seconds clip actual intervals at local midnight boundaries (including DST), plus capped active work. Session count means focus sessions **started** in the period, including active/paused/stopped/completed. A cross-midnight session can contribute time to a day in which it did not start. UI cards round minutes down; table/API retain seconds. Trends are seven actual daily counts with a text/table alternative and an insufficient-history caveat. Categories reflect current assignment, not historical assignment. Streak summary is the longest current/best streak among current daily tasks; total daily completions includes non-deleted converted tasks' historical daily facts.

Archived task facts and associated focus sessions are excluded from insights. General unassociated focus remains. XP/badges remain after task archive; account deletion cascades all new tables. Existing private task archive retention is unchanged. Reward derivation currently scans the owner's historical facts; large histories may require incremental aggregates in a future measured optimization. Public histories remain bounded by existing endpoints; no unbounded ledger response is exposed.

## Verification

`apps/api/tests/test_progress.py` uses real disposable PostgreSQL and explicit records for concurrency, rollback, toggle/retry, configurable immutable awards, backfill/all badges, focus cap/eligibility, deletion/cascades, zero denominator, 50% and 12.5% rates, idle schedule snapshots and local-midnight/DST bounds. Browser `apps/web/tests/progress.spec.ts` verifies empty/populated/reload/error recovery, rates/badge/XP, deletion, axe and 360/768/1440 widths through the normal disposable runner.
