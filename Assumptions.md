# Devtreck assumptions register

## Phase 8 updates

A-08 implemented: max3 daily priorities, 25/5 presets, one active/paused session and no automatic task/parent completion. A-41: owner/local-date plan arrays validate against current Today and show at most500 with explicit truncated/missing workload labels (recommendation, implemented). A-42: focus targets persist per session; new form defaults reset after reload, natural completion materialized at calculated deadline on next read (recommendation, implemented). A-43: command-key/fingerprint idempotency and recorded active intervals govern totals; paused/break time excluded (recommendation, implemented). A-44: checklist max100, exact-set atomic reorder, confirmed UI delete and parent progress refresh (recommendation, implemented). A-45: Focus polls every3 seconds, associations offer first100 active tasks plus General; history pages10 in browser (recommendation, implemented). Separate concurrent password-policy source edit is preserved outside phase 8 scope/commits.

## Phase 7 updates

A-36: protected Today/All/Daily routes share six-view workspace; 10 tasks per page, bounded histories/categories and expandable filters (recommendation, implemented). A-37: writes require server confirmation before refreshing totals; no optimistic streak/counter changes (recommendation, implemented). A-38: dashboard counts actual completion facts, including reopened first completion; archived task facts excluded from display totals (recommendation, implemented). A-39: timed deadlines entered explicitly in device zone and displayed in account zone; calendar-only dates keep account-day semantics (recommendation, implemented). A-40: native edit/detail/delete/category dialogs with private archive notice and category-uncategorizing confirmation (recommendation, implemented). Optional reminder UI, planning priorities, focus, checklists and rewards remain deferred.

## Phase 6 updates

A-02 device timezone suggestion now requires explicit Save in Settings; account default remains UTC. A-13 light/dark/system theme now persists in profile. A-32: same-origin Next rewrite to server-only API_ORIGIN, no browser persistent credential storage (recommendation, implemented). A-33: protected server profile checks plus client focus/navigation/minute revalidation catch session revocation (recommendation, implemented). A-34: native deletion confirmation dialog with current password and acknowledgment, only completed Overview/Settings navigation linked (recommendation, implemented). A-35: browser tests use random disposable PostgreSQL database and isolated ports 8010/3100 (recommendation, implemented).

## Phase 5 updates

A-02 history/boundary rules implemented for configured IANA zones; browser suggestion remains phase 6. A-10 implemented: fresh UUID daily epochs, current reset on reactivation and lifetime best across separate runs without bridging. A-28: one local-day credit per task across epochs; older-epoch today credit remains visible but cannot start the new run (recommendation, implemented). A-29: westward-zone future-labeled facts retained, excluded from current run until their local day arrives; lifetime best/history retained (recommendation, implemented). A-30: global daily status pending after completion, separate today_completed occurrence metadata and dynamic views (recommendation, implemented). A-31: separate bounded one-time /history and all-epoch /daily-history; cache reconciliation derives from facts (recommendation, implemented).

2026-11-07. Proposed means not user-approved. Phase 1 foundation is now implemented under the submitted prompt. Resolve material decisions before the affected implementation, while independent work continues.

| ID | Assumption | Why | Source | Impact if wrong | Approval/checkpoint | Status |

|---|---|---|---|---|---|---|

| A-01 | Same-origin opaque cookie sessions with CSRF protection | Secure revocation and no browser token storage | Recommendation | Deployment/proxy and session schema | Before phase 3 | proposed |

| A-02 | Browser-suggested valid IANA zone, user confirms; UTC fallback; later changes affect future boundaries only | Requirements 7 timezone history | Requirement + recommendation | Streak/date UX | Before phase 5 | proposed |

| A-03 | Archive deleted tasks/history until account deletion; no restore UI initially | Retain analytics and immutable evidence; explicit confirmation | Recommendation | Retention/storage/privacy | Before phase 4 | proposed |

| A-04 | Reopen one-time task preserves first completion and cannot re-earn XP; daily reopen cannot undo qualified history | Prevent history corruption and reward exploits | Recommendation | Task UX/rewards | Before phase 4 | proposed |

| A-05 | Include all section 8.1–8.5 productivity features; defer reminders/email/reset, freezes, custom recurrence, exports, calendars, mobile and admin | Requirements 2.1 and optional labels | Requirement interpretation | Release size | No blocking approval | proposed |

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

## Phase 4 updates

A-03 implemented default: task rows/content/history archived privately until account deletion; no restore UI. A-04 implemented: one-time reopen/recomplete preserves one lifetime first-completion fact. A-06 implemented: custom category CRUD, owner constraints and mutually exclusive calendar-date/timed deadlines. A-10 foundation: type audit rows and daily activation timestamp; full streak engine remains phase 5. A-25: category names unique per owner/case-sensitive, titles max200, description max10000, estimate 1–10080 minutes (recommendations, implemented). A-26: list default active, explicit completed view/status, limit25/max100 and offset<=10000; escaped substring search (recommendation, implemented). A-27: deletions require confirm=true query, task archives and category SET NULL with deferred owner constraint (recommendation, implemented). No daily completion enabled in this phase.
