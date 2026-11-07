# ADR-0005: Immutable daily facts and activation epochs

Status: implemented under phase 5 authorization, 2026-11-07.

Separate daily_completions from one-time completions to preserve phase 4 source facts. Unique (task_id,completion_day) spans all epochs. Composite task/owner FK and account cascade protect ownership/privacy. Store UUID epoch, UTC-aware server instant, local day and IANA zone-at-completion. Migration assigns existing daily tasks fresh epochs and zero credit without changing earlier data.

Framework-free clock/calendar rules calculate current from active epoch and lifetime best from maximum run within any epoch. Calendar dates, not duration, govern streaks. Caches are nonauthoritative; public responses derive fresh values, missed-day reset needs no scheduler, and authenticated reconciliation repairs drift.

User-before-task lock order serializes timezone edits and independent completion transactions. Read owner zone after lock, then sample trusted clock. Atomic insert-on-conflict and DB uniqueness prevent duplicate local-day credit. New fact/cache changes commit together. No client-supplied clock/epoch/counter is trusted.

Type conversion starts a new epoch without rewriting facts. Global daily status stays pending; nested today_completed represents occurrence state. Reopen preserves credit. Same-day older epoch credit cannot create a new epoch's run. Westward-zone future-labeled facts are retained but excluded from current run until applicable; lifetime best/history remain visible.

Alternatives: only counters cannot reconcile; timezone-based historical rewrites corrupt evidence; midnight jobs add failure modes; merging daily/one-time facts risks earlier first-completion identities. Consequences: epoch-aware reads and historical summary work. Bounded-page summaries batch queries; optimize further only from measured load.

Official Python zoneinfo documentation checked. Existing locked tzdata is now an explicit direct dependency for Windows portability. No dependency upgrade required.
