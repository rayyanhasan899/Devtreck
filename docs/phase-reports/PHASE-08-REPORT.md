# Phase 08 report — Daily planning, focus and checklists

Date: 2026-11-07, Asia/Karachi. Status: **PASS WITH KNOWN LIMITATIONS**.

## Objective and actual features

Daily plan in Today and its own protected navigation route: current actionable tasks, at most three top priorities, persisted owner/local-date manual order, reset to explainable suggested order, estimated workload and explicit missing/truncated estimate labels. Suggestions consider overdue, due date, priority and duration. Completed/archived tasks leave the actionable plan without rewriting history.

Focus route: configurable focus/break preset25/5, task-linked or general session, start/pause/resume/stop, server-recovered state after refresh/navigation and multi-tab polling. Session history and daily/trailing-seven-local-date focus time persist. Active intervals cap at configured target; paused gaps and break time excluded. Timer completion never completes a task. Terminal state is materialized on next server read/command at calculated deadline, so offline time cannot inflate duration and no background worker is needed.

Checklists in task details: add/edit/complete/delete with confirmation and keyboard Up/Down ordering. Parent progress appears in detail and task card after close; all items complete does not complete parent. All endpoints inherit parent/task ownership and account privacy policy.

## Requirements and changed files

PLN-01–06: productivity service/repository and daily-plan UI. FOC-01–07: focus model/events/intervals, state machine, history/totals and focus UI. SUB-01–06: checklist schema/CRUD/reorder/parent progress and detail UI. SEC-02/NFR-07: owner-scoped access, composite FK, one-active partial unique index, command-key uniqueness, transactional user locks and reorder invariants. Existing account/task/streak behavior remains.

Added domain/productivity.py; persistence/productivity.py; services/productivity.py; presentation/productivity.py and productivity_schemas.py; migration e5fe82dd46cc; tests/test_productivity.py. Extended models, main composition, task progress queries/contracts/rendering. Added browser Focus/Plan routes, focus/checklist/plan components and productivity browser journey. Extended navigation, styles, task detail/card, typed task contracts and contextual API errors. Added ADR-0008/API guide and updated README/assumptions/report. No files deleted; no dependency upgrades/installations.

Migration adds daily_plans, checklist_items, focus_sessions, focus_events and focus_intervals, with ownership/cascade/unique/check/index constraints. Existing data untouched. Plan IDs are validated against current owned eligibility on write and intersected on read; JSON cannot expose another owner's task. Checklists use deferred unique parent/position. Focus task association uses composite owner FK plus task SET NULL handling. Account deletion cascades all new owned records.

ADR-0008 records server interval authority, idempotent commands, bounded plans/checklists and no automatic parent completion. A-08 progressed; A-41–45 record 500-item plan window, session target persistence/default controls, interval totals, max100 checklist items and Focus polling/history bounds. Separate password-policy work is outside phase scope.

## Verification and evidence

Retained existing Python3.14.7, SQLAlchemy2.1.8, Alembic1.20.1, PostgreSQL18.6, Node24/Next16.4.5/React19.3 and locked tooling. No new services or dependencies required.

- Full backend pytest: **59 passed**, no skips/warnings. Six new productivity tests cover checklist CRUD/exact-set reorders/ownership/progress/no parent completion, plan suggestion/manual order/priorities/workload/privacy, clock-controlled focus pause/resume/cap/midnight summary/break exclusion, session ownership/idempotency/one-active behavior, concurrent focus starts/checklist reorders and account deletion cascades.
- Final focused productivity rerun: six passed after ensuring plan task DTOs also include true checklist progress. Clock tests prove120 seconds total despite a100-second pause and late return,90 seconds attributed after midnight, no break inclusion and no task completion. Concurrent independent sessions return one focus ID and one persisted session/event sequence.
- Ruff check/format passed (47 Python files); mypy passed (40 application modules); pip check passed.
- Frontend lint, strict type checks, production build passed. /app/focus and /app/plan generated as protected dynamic routes. npm audit: zero vulnerabilities.
- Full real browser suite: **six journeys passed** (three account, two task, one productivity),56.1 seconds. Productivity checks plan priority/order persistence, missing estimates, checklist creation/checking/reorder/parent progress, focus task association, pause/reload, second-tab resume, stop/history, unchanged task, break start, axe and360px layout.
- Final focused browser rerun expanded checklist coverage to edit, cancel-delete and confirm-delete: passed in15.3 seconds. The prior full-suite results remain evidence for unchanged account/task flows.
- Axe Focus scan: zero violations. Desktop/mobile screenshots visually inspected; no horizontal overflow at360px. Existing task tests retain360/768/1440 coverage. Test artifacts contain only disposable synthetic accounts and are ignored.
- Migration round-trip/schema agreement tests passed in generated disposable databases. Local development alembic upgrade head/check/current passed at e5fe82dd46cc with no drift. No valuable database reset or production operation.
- Production API/web refreshed at8002/3000. Live OpenAPI exposes plan and focus routes; readiness200; Focus through web proxy rejects anonymous requests401 and protected Focus page redirects to login. Production build/HTTP smoke are separate from development-server browser journeys.

## Failures and fixes

Initial migration generation omitted PostgreSQL JSONB import and generated duplicate names for composite/simple focus task FKs. Added explicit import/owner-constraint name; disposable upgrade/downgrade/check now pass. Ruff/import/unused-variable issues corrected.

Browser checks caught ambiguous visible/hidden plan-title selectors and exact session-type labeling; fixed selectors/labels. Native checkbox check expected an immediate optimistic state; changed to click then await server-confirmed checked state. A real pending-add issue could clear a next-item draft: checklist input now disabled during save and test awaits each confirmed item. Focus responses use a request version so stale polls cannot overwrite newer command recovery. Plan save uses the sampled local-day metadata, avoiding a second-clock midnight mismatch. Checklist deletion now requires confirmation. Final relevant checks pass.

## Security, data and limits

All new private routes reuse session, Origin and CSRF checks. No client-supplied authoritative timestamps/durations/counters or user IDs. Focus command key/fingerprint binds each action/config/session and rejects changed-payload replay; one active/paused session enforced by database. User-before-resource locks serialize writes, timezone sampling and concurrent state transitions. Intervals and record IDs provide future reward/analytics provenance without implementing XP now.

Tests operate only on guarded random databases via separate devtreck_test service and clean their own processes/data. Local additive migration leaves original account/task data intact. No secrets printed/committed; server access-log policy unchanged.

Known limits: Windows Chromium and local checks verified; hosted CI/Linux/full browser matrix not claimed. Plans show at most500 tasks with explicit estimate caveat; checklist cap100 and associated-task selector first100 active tasks are disclosed. Focus new-session form preferences reset25/5 after reload, while an existing target/state persists. Browser countdown is an estimate reconciled every3 seconds; server intervals remain authoritative. Whole-minute summary cards round down; history/API preserve seconds. Natural terminal materialization occurs on read rather than background notifications. Rewards/levels/achievements/insights remain phase9; external notifications and custom recurrence remain deferred.

## Git, concurrent work and handover

Branch codex/phase-08. b2aefd7 implements features/migration; f3e9aab adds productivity tests; final documentation commit records evidence. Main/private origin preserved; no push/PR/merge/history rewrite.

Independent password-policy changes appeared during the work: apps/api/app/presentation/account_schemas.py, apps/web/src/components/auth-form.tsx and apps/web/src/components/settings.tsx lower the minimum from12 to8. They were preserved and deliberately excluded from phase8 staging/commits. Tests/build used the current workspace; phase8 itself does not change password policy. These three files remain modified, so the final working tree is not wholly clean.

No manual setup action required. **Usable now:** all previous account/task/habit features, Daily plan priorities/manual order/estimates, Focus and Break sessions with pause/resume/stop/recovery/history/totals, and task checklists/progress/reordering. Open http://127.0.0.1:3000. Phase9 has not started.
