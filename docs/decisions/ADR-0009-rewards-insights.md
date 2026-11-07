# ADR 0009: Source-based rewards and coverage-aware insights

Status: implemented for phase 9 under the submitted phase prompt; no additional approval required.

Use existing immutable completion IDs and authoritative focus intervals rather than client counters. The minimal append-only XP ledger and unique achievement keys survive task archive but cascade with account deletion. Serialize per-user derivation and include grants in the completion transaction. Store amounts, rule fingerprint and local reward date rather than revaluing earned XP. Record cap skips so later zone changes do not re-award rejected sources.

Separate completion activity from eligible occurrence snapshots. Snapshot daily schedules before edits and materialize idle dates while their schedule is still known. Freeze first observed due one-time occurrences. Record coverage explicitly; incomplete historical schedules and zero denominators yield unavailable rates. This trades an initially unavailable weekly rate for truthful reporting. Current-category grouping and original qualifying daily dates are labeled. No chart infers a trend from sparse data.

Use a semantic Progress page with server-derived numbers, accessible table alternatives, main/skip landmarks, loading/error/retry and local-zone badge dates. No dependency or external analytics service is introduced. See [contract and tradeoffs](../api/progress.md). Owner-history derivation may later be replaced by measured incremental aggregation without changing source uniqueness or provenance.

Official compatibility reference checked 2026-11-07: [SQLAlchemy 2.1 PostgreSQL INSERT / ON CONFLICT](https://docs.sqlalchemy.org/en/21/dialects/postgresql.html). Existing installed SQLAlchemy2.1.8 supports the chosen dialect insert. Installed Next16.4.5 server/client component guide was read before UI changes. Dependency locks remain unchanged.
