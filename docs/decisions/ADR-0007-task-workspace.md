# ADR-0007: Confirmed task workflows and server-owned dashboard counts

Status: implemented for phase 7, 2026-11-07.

Today, All tasks and Daily habits are protected server routes mounting a shared task workspace; all six views remain available inside the workspace. Explicit Pydantic contracts and central client connect existing task/category/streak/history services. No business counters or streak rules move into the browser.

Add /api/dashboard for actual owner-scoped counts: actionable Today, outstanding pending/in-progress occurrences, recorded completions today and credited daily habits out of active habits. One-time completion timestamps use current IANA day's UTC bounds; daily facts use stored local-day labels. Archived records excluded. Reopening preserves a recorded completion and therefore does not subtract it from Completions today. No database schema/index change justified by this workload.

Task/category writes wait for server confirmation before list/summary invalidation. Failed writes preserve actual saved state and display retryable error; stale list requests cannot overwrite newer state. Refresh on focus/minute is suspended while dialogs are open. Views/filter changes reset offset; search is explicit, bounded and cleared visibly with view changes. Ten tasks per page; histories page by 25 and categories load in bounded 100-row batches.

Native dialogs support keyboard focus, cancellation and delete confirmation. Archive retention is disclosed; category delete leaves tasks uncategorized. Editor distinguishes calendar date from timed instant; date-only stays in account zone, timed entry explicitly uses device zone and displays in account zone. Status completion remains a separate server operation. Daily occurrence completion uses today_completed and disables repeat action while showing current/best streak and immutable history.

Alternatives: browser-derived dashboard totals are misleading under pagination; optimistic completion can falsely display unsaved streaks; loading every task defeats bounded queries. Consequences: additional aggregate reads and explicit refresh states, but trustworthy feedback and shared UI across views. Optional reminders, smart priorities, focus, rewards and insights remain later scope.
