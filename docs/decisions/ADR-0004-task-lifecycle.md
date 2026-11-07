# ADR-0004: Owner-scoped task lifecycle and immutable first completion

Status: implemented in authorized phase 4, 2026-11-07.

Use owner-scoped repository queries plus composite foreign keys. Categories have unique (id,user_id); tasks reference this pair to prevent foreign-category assignment even through direct persistence. A separate category_id FK applies SET NULL on category deletion. Composite ownership validation is deferred to commit so deletion can detach tasks before the owner-pair check. Task and completion/type audit pairs enforce the same owner. User deletion cascades all owned data.

Keep date-only due_date distinct from timezone-aware due_at; mutually exclusive effective deadlines. Apply current user timezone for calendar views and date-only overdue, UTC instants for timed overdue. No remote scheduler needed. Literal substring search escapes wildcard characters; allowlisted sorting and bounded pagination stay in persistence. Domain TaskQuery is framework-free; application service owns lifecycle/transactions; routes validate and serialize Pydantic contracts.

Archive task rows/content/history until account deletion, hidden from active APIs. No restore UI initially. Category deletion is permanent after confirm; tasks remain uncategorized. This implements the proposed retention default in A-03; no production retention promise beyond documented account deletion.

Store one immutable first-completion fact per one-time task, unique on task ID; reopen changes only current status and cannot farm repeated facts. Phase 9 rewards must reference this source. Type edits append audit rows, reset status pending and set a fresh daily activation timestamp without rewriting historical completions. Daily completion/streak logic remains phase 5; its schema should use separate daily occurrence facts or a carefully reviewed migration preserving these first-completion facts.

Alternatives: hard-delete history loses useful integrity/reward evidence; one deadline timestamp alone invents time for date-only tasks; relying only on frontend ownership permits resource-ID substitution. Consequences: archived data consumes storage until account deletion and all queries must exclude it. Case-sensitive category names permit Work/work; no extra tag system or reminder infrastructure added.

Reference checked: https://docs.sqlalchemy.org/en/21/core/constraints.html. Existing dependency locks retained.
