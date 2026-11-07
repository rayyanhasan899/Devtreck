# Productivity APIs and usage — phase 8

Browser: Today → Plan your day, or Daily plan navigation; Focus navigation; click any task title for Checklist. Normal account cookies, approved Origin and X-CSRF-Token protect writes. The shared browser client supplies these. No user IDs, clocks or authoritative duration values are accepted from clients.

## Daily planning

GET /api/plan/today returns current local day/zone, ordered task contracts, top priority IDs, suggested order/reasons, estimated minutes, missing estimate count, total and truncation flag. PUT accepts order_ids and priority_ids; priorities max3, all IDs unique/current/owned. Empty order restores suggested ordering. Plans are per local date; midnight/new timezone day uses that day's plan. Completed/archived tasks leave the actionable plan without rewriting historical task facts.

Ordering: overdue first, due calendar date, high/medium/low priority, shorter known estimate before unknown, stable ID tie break. Manual order overrides suggestions; top flags remain separately selectable. Max500 task window; estimates explicitly cover shown tasks when truncated. Missing estimates are labeled, never silently treated as zero workload.

## Checklists

GET/POST /api/tasks/{task_id}/checklist lists/adds items. PATCH/DELETE /api/tasks/{task_id}/checklist/{item_id} edits title/completed or removes item. PUT /api/tasks/{task_id}/checklist-order accepts ids containing every current item exactly once. Unknown/foreign/archived parent or foreign child returns 404; stale/missing/duplicate reorder conflicts with no partial update. Titles trimmed 1–200, max100 items. Task responses expose checklist_total/checklist_completed; detail UI refreshes parent card when closed. Native buttons provide keyboard Up/Down, rename, complete and confirmed deletion. Parent completion always explicit.

## Focus

POST /api/focus accepts key (UUID idempotency key), optional owned task_id, kind focus|break, seconds (focus60–10800, break60–3600). Defaults focus1500 seconds; browser preset25/5 minutes. POST /api/focus/{id}/pause|resume|stop accepts key. One active OR paused session per user; starting another conflicts. Same key/payload never repeats effects; reusing key for another action/session/config conflicts. Terminal sessions remain terminal.

GET /api/focus/current recovers active/paused state; /focus/history?limit=25&offset=0 returns bounded history (max100), /focus/summary returns actual focus seconds today and trailing seven local dates, with reporting period/zone. Session responses carry association, status, configured target, server-derived elapsed, start/end and server_now. Active browser countdown is only a display estimate; server intervals decide saved time.

Pauses and breaks excluded. Stops retain actual worked time with stopped status; reaching target records completed at calculated deadline, even if the browser was closed until a later read. No task completion or automatic break start. Select Break and start explicitly. New-session input preferences reset25/5 after refresh; an existing session's saved target/elapsed/state always survives. UI polls every3 seconds and on focus for multi-tab reconciliation. Network failures show errors; command keys reused on retry within page, and reload recovers actual session state. Very large task lists show first100 active association options, with General focus always available.

Daily/week summaries count seconds, browser cards show whole minutes rounded down and history shows seconds. Cross-midnight intervals are split against IANA boundaries; no 24-hour assumption. Stopped/completed/ongoing focus intervals contribute actual work; no competition, XP or badges yet.

## Verification

Run API pytest and the disposable browser runner as documented in testing guides. Focus clock is injectable only through backend test dependencies. Tests advance trusted test time without sleeping for timers, proving pauses, capping, midnight splits, duplicate/concurrent commands, single active session, break exclusion and no parent auto-completion. Browser journey covers persisted planning order/top flags, checklist progress/reorder, focus pause/reload, second-tab resume, stop/history, break start and mobile/axe checks.
