# ADR-0008: Daily plans, focus intervals and parent-owned checklists

Status: implemented under phase 8 authorization, 2026-11-07.

Daily plans use owner/local-calendar-day keys and bounded UUID order/priority arrays in PostgreSQL JSONB. Every submitted ID must be among that owner's current actionable Today tasks, with no duplicates and at most three priorities. Reads intersect persisted IDs with currently eligible owner tasks, so completion/archive/timezone changes cannot disclose foreign or stale content. No copied task titles in plan storage. Suggest overdue/deadline/priority/duration order with visible reasons; user order wins. Maximum 500 shown; truncated workload is explicitly labeled, including missing estimates.

Focus uses a user lock, session state machine, partial unique active/paused index, unique owner/command key, immutable command fingerprint and recorded active intervals. Start/pause/resume/stop commands are transactional. Same-key retries return current authoritative session without repeating effects; changed payload with reused key conflicts. Repeated state commands are harmless no-ops. Session durations are bounded and server-controlled; no browser timestamps or final counters accepted.

Elapsed time is the sum of active intervals, capped at configured target. Pause closes an interval; resume begins another. At or after the deadline, the next server read/command materializes completion at its exact calculated deadline, so a background worker is unnecessary. Break intervals and paused gaps never enter focus totals. Daily/trailing-seven-local-day totals clip actual intervals at timezone-aware midnight boundaries. Focus completion never writes task status. Defaults 25/5 minutes; configurable per session, target persists across refresh, new form preferences reset to defaults after page reload.

Checklists inherit parent ownership and lifecycle through composite FK. Parent/user locks and deferred unique parent/position constraint make reordering atomic. Maximum 100 items; reorder must contain the exact current set once. Completing all items cannot complete parent. API computes progress in batches for task lists. Account deletion cascades plan, focus/event/interval and checklist data; task archive hides checklist endpoints and preserves focus association/history.

Alternatives: browser-only timers lose state on refresh; client durations are manipulable; Redis/queues add unnecessary infrastructure; generic nested task trees exceed checklist scope. Consequences: explicit server polling while Focus is open, opportunistic terminal materialization, bounded plan/checklist workflows and separate focus/task state.

No new dependencies. Existing SQLAlchemy/PostgreSQL constraints and Python timezone facilities are used. Broader rewards/analytics remain phase 9.
