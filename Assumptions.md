# Devtreck assumptions register

2026-11-07. Proposed means not user-approved. Phase 1 foundation is now implemented under the submitted prompt. Resolve material decisions before the affected implementation, while independent work continues.

| ID | Assumption | Why | Source | Impact if wrong | Approval/checkpoint | Status |
|---|---|---|---|---|---|---|
| A-01 | Same-origin opaque cookie sessions with CSRF protection | Secure revocation and no browser token storage | Recommendation | Deployment/proxy and session schema | Before phase 3 | proposed |
| A-02 | Browser-suggested valid IANA zone, user confirms; UTC fallback; later changes affect future boundaries only | Requirements 7 timezone history | Requirement + recommendation | Streak/date UX | Before phase 5 | proposed |
| A-03 | Archive deleted tasks/history until account deletion; no restore UI initially | Retain analytics and immutable evidence; explicit confirmation | Recommendation | Retention/storage/privacy | Before phase 4 | proposed |
| A-04 | Reopen one-time task preserves first completion and cannot re-earn XP; daily reopen cannot undo qualified history | Prevent history corruption and reward exploits | Recommendation | Task UX/rewards | Before phase 4 | proposed |
| A-05 | Include all section 8.1â€“8.5 productivity features; defer reminders/email/reset, freezes, custom recurrence, exports, calendars, mobile and admin | Requirements 2.1 and optional labels | Requirement interpretation | Release size | No blocking approval | proposed |
| A-06 | Use categories rather than parallel tag system; custom category CRUD; date-only deadline distinct from instant | Simpler allowed category/tag alternative and accurate dates | Recommendation | Schema/filter semantics | Before phase 4 | proposed |
| A-07 | Synchronous SQLAlchemy with sync FastAPI routes initially | Reduce needless async complexity | Recommendation | Throughput strategy | No blocking approval | proposed |
| A-08 | Three top priorities; 25/5 focus preset; one active session; no automatic task/parent completion | Bounded understandable workflows | Recommendation + requirements | Planning/focus UX | Before phase 8 | proposed |
| A-09 | XP and analytics formulas as phase 9; retain minimal reward ledger for deleted tasks without task content | Transparent idempotent rewards and defined denominator | Recommendation | Behavior and retention | Before phase 9 | proposed |
| A-10 | New daily activation epoch on type conversion; historical daily facts remain immutable | Avoid bridging unrelated recurrence periods | Recommendation | Streak expectations | Before phase 5 | proposed |
| A-11 | Production host/domain/budget unselected; same-origin container deployment proposed | No external resources authorized | Inference | Release cannot claim live deployment | Required before external deployment | proposed |
| A-12 | Use apps/web + apps/api, npm and venv; select versions only after compatibility verification | Repository contains no implementation | Architecture guidance + recommendation | Tooling portability | No blocking approval | proposed |
| A-13 | Slate/teal restrained UI with light/dark/system, semantic components and reduced motion | No branding supplied | Recommendation | Visual direction | No blocking approval | proposed |
| A-14 | Source files remain at supplied external paths during planning; phase 1 copies reviewed sources into repo after checking duplicates | Planning boundary permits only listed planning outputs | Inference | Fresh-clone portability | No blocking approval | proposed |
## Phase 1 updates

A-12 implemented with Node 24/Python 3.14 and pinned dependency locks. A-13 applied to landing with system light/dark themes and override tokens; user settings arrive in phase 6. A-14 fulfilled: unchanged source documents copied into checkout. Other product proposals remain proposed. A-15: PostgreSQL 18.6 on loopback 5433/5434 with independent test storage (recommendation, implemented; change if port conflicts). A-16: system fonts avoid network build dependency (recommendation, implemented).

## Phase 2 updates

A-07 implemented: synchronous request-scoped sessions/routes with explicit commit/rollback. A-17: initial user/session schema supports later authentication; token hashing/expiry enforcement and full account validation are phase 3 (architecture recommendation, implemented foundation; security behavior incomplete until that phase). A-18: disposable integration databases use a CREATEDB test role, never a production role (recommendation, implemented). A-19: lowercase/trim normalization across entire email with unique DB check (requirements + proposed normalization rule, implemented foundation; account behavior in phase 3). A-20: unversioned public health/readiness with typed success bodies and error envelopes, no redundant success envelope (recommendation, implemented). A-01 remains a proposed account-session strategy; schema support does not imply user approval or completed authentication.

## Phase 3 updates

A-01 implemented as explicitly specified by the submitted phase prompt: opaque server sessions/CSRF cookies. A-17/19 implemented for account APIs and normalized email. A-21: seven-day absolute sessions, 12–128-character passwords, current-password proof for email/password/delete and session invalidation on email/password changes (security recommendations, implemented). A-22: register directs user to login; no delivery/recovery/notification settings until provider exists (requirements option/recommendation, implemented). A-23: fixed ten-minute DB counters with limits documented in accounts guide and opportunistic stale cleanup (recommendation, implemented). A-24: default local API inspection origin port 8002; production must configure explicit HTTPS origins (recommendation, implemented). Full streak timezone-change/history policies remain phase 5; profile zone validation alone does not implement them.
