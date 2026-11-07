# Daily completions and streaks — phase 5

Use http://127.0.0.1:8002/docs with normal session cookie, approved Origin and X-CSRF-Token for mutations. Daily task responses/list items include nested streak metadata; one-time tasks have streak:null. Fields: current_streak, best_streak, today_completed, last_qualified_day, total_completions, current_day and time_zone. Never submit a day, timestamp, epoch or counter; the server decides these.

## Actions

- Create task_type:daily. Current and best start zero; creation earns no credit.
- POST /api/tasks/{id}/complete or PATCH status:completed records one daily credit for the current server instant in profile IANA zone. Retries/concurrent same-day requests return the existing effective result.
- Global daily status becomes pending after complete; occurrence state is streak.today_completed. A habit must not become permanently completed.
- POST /api/tasks/{id}/reopen or PATCH pending cannot erase today's qualified credit. No backdating, undo-credit, recovery or freeze.
- GET /api/tasks/{id}/streak derives live counters. POST /api/tasks/{id}/streak/reconcile repairs stored caches from history with normal mutation security. One-time tasks return 409 on streak endpoints.
- GET /api/tasks/{id}/daily-history?limit=25&offset=0 returns id, epoch, completion_day, completed_at, time_zone for all retained daily activations, newest first. Max100, offset<=10000. Accessible after changing type to one-time. Original /history separately preserves one-time completion facts.

Daily view and All retain completed-today habits. Today excludes completed-today daily tasks even with old deadlines; they reappear on the next local day. Completed view/status includes today's qualified daily tasks and completed one-time tasks. Pending/in-progress filters exclude already-credited daily occurrences.

## Rules and recurrence epochs

First completion=1; consecutive local date increments. Yesterday credited and today pending preserves the run until today's end. Missing yesterday resets current to zero immediately on read; best stays. A new completion after a gap starts at one. Midnight is a calendar boundary, not elapsed 24 hours; DST days can be 23/25 hours.

Trusted UTC clock is dependency-injected for tests only; no public clock override exists. Stored counters can age at midnight, but public responses derive fresh values from immutable facts. Reconcile repairs caches without manufacturing records.

Changing daily to one-time ends the active epoch and retains history. Switching back creates a fresh epoch with current zero. Lifetime best is maximum run across individual epochs; epochs never bridge. Task/local-day uniqueness spans epochs: toggling type cannot earn another same-day credit. If an older epoch credited today, today_completed stays true while the new epoch's current remains zero until a new qualifying day. One-time history remains untouched.

## Timezone changes

Profile edits and completions acquire the same user lock. Completion then locks task, reads fresh zone and samples server time. Future dates use new zone; historical timestamp/day/zone remain unchanged.

A zone change can make current local day differ from latest stored label. After westward travel, future-labeled history remains visible and contributes to lifetime best, but does not advance current run until that date arrives. last_qualified_day is the maximum recorded calendar label, possibly ahead of current_day. Current uses active-epoch facts no later than current_day. Returning to an already credited task/date cannot duplicate credit. Distinct zones can yield different dates a short time apart; no hidden rolling-24-hour rule is imposed.

The future settings UI must explain this effect. API already exposes current_day/time_zone and historical zone provenance; this guide supplies the notice now. Optional recovery/freeze remain deferred.

Archived histories remain hidden; account deletion cascades daily facts. Every streak/history/reconcile operation enforces ownership. List summaries batch histories for one bounded task page instead of one query per task. Further large-history optimization should follow measurement.
