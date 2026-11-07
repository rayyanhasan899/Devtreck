# Phase 06 report — Browser foundation and account experience

Date: 2026-11-07, Asia/Karachi. Status: **PASS WITH KNOWN LIMITATIONS**.

## Objective and implemented behavior

Functional landing signup/sign-in links, registration/login forms, protected responsive application shell, account overview, Settings, profile/name/timezone/theme updates, reauthenticated email/password changes and confirmed account deletion. Sign out works on desktop and mobile. Only completed Overview/Settings screens appear in private navigation; task/habit UI is intentionally phase 7.

Central typed API client handles same-origin session cookies, fresh CSRF headers, no-store requests, safe validation/network/server errors and expired sessions. Next.js rewrite proxies /api to server-only API_ORIGIN. Server profile checks protect layout/pages before returning private content; client focus/navigation/minute checks detect revocation without a new layout mount. Wrong current password is distinguished from an expired session by checking profile validity. No credentials/tokens persist in browser storage.

Forms use semantic labels, native validation, field feedback, status/alert messages, duplicate-submit refs and disabled pending controls. Deletion uses native modal focus trapping, Escape/cancel, explicit acknowledgment and current-password proof. Profile themes persist in the backend and apply light/dark/system tokens. Device timezone is an explicit suggestion confirmed by Save; history-boundary notice appears beside the input. Error boundary/retry and workspace loading state cover service failures. No email delivery/recovery or unconfigured notification controls.

## Requirements, architecture and files

ACC-01–21 browser contributions: auth forms and protected pages consume existing account contracts; complete profile/security/deletion journeys use backend ownership/session policies. UI-05–13: confirmation, async feedback, required/validated fields, guarded submission, responsive layouts, keyboard focus/skip link, contrast, timezone display and settings. NFR-02/05–06/10–13/19: client navigation, honest save results, mobile usability, semantic controls and browser checks. These phase contributions do not claim future task-form interactions are complete.

Added web login/signup routes, protected app layout/overview/settings/loading, shared error boundary, auth/shell/settings components and browser/server profile clients. Extended landing, CSS tokens, root layout formatting and Next rewrite configuration. Added Playwright configuration/journeys, isolated Python browser runner, dev dependencies/lock updates and browser CI job. Extended ignored test artifacts and env example. Added ADR-0006/testing guide, README/assumptions/report updates. No files deleted, no API business-rule changes or schema migration.

ADR-0006 explains same-origin proxy, protected fetching, no browser credential persistence, native dialog and isolated browser database/process lifecycle. A-02/A-13 progressed; A-32–35 record proxy, revalidation, usable navigation/confirmation and test isolation. Existing source requirements/master plan/prior report guided implementation; installed Next.js server/client, cookies and rewrites docs were read after resolving their actual .md paths.

## Verification and evidence

Retained Next.js 16.4.5, React 19.3.0, Node 24.15.0 and existing Python/database stack. Added pinned Playwright 1.65.0 and locked axe tooling; installed its Chromium runtime. Frontend source formatted with Prettier; package lock pins new dependency tree.

- From apps/web: npm run lint, npm run typecheck, npm run build passed. Dynamic protected /app and /app/settings routes generated correctly; signup/landing static. npm audit: zero vulnerabilities.
- From apps/api: Ruff lint/format and mypy passed; Python test suite **52 passed**, no skipped tests or warnings. Final formatting includes browser runner (40 files); application typing covers 34 modules.
- Root browser runner executed **3 real browser journeys, all passed** in final run (33 seconds). Temporary API/web ports 8010/3100 and generated disposable PostgreSQL database; valuable local account records untouched. Services and random database cleaned after run.
- Browser journey 1: registration/login, settings/name/timezone/theme persistence across refresh, dark theme, axe accessibility, modal Escape/cancel, email change and re-login, password change and re-login, confirmed deletion and protected redirect.
- Journey 2: unauthenticated protected navigation, invalid-login feedback, real backend session revocation through second API context, focus-driven expired-session notice/redirect.
- Journey 3: keyboard skip link, mobile signup accessibility, settings mobile accessibility, 390px mobile and 768px tablet no-overflow checks, screenshots, failed PATCH network request shows error without saved state, reload restores actual stored name, logout/protected navigation.
- Axe scans found zero remaining violations on checked signup/settings states. Desktop 1280px, mobile 390px and tablet 768px screenshots were visually inspected; layouts readable and controls fit. Generated screenshots are ignored local test artifacts.
- Production web restarted on 127.0.0.1:3000. Live /login returned 200 with form; unauthenticated /app/settings redirected to /login. Existing API remains at port 8002. Production build/HTTP smoke verified separately from development-server browser journeys.
- git diff --check passed before commits; no schema changes, production migration, deployment, push or PR.

## Failures resolved

Initial docs reads used nonexistent .mdx filenames; found/read installed .md guides. Automatic review rejected a long combined shell file-write; explicit file patches completed the work safely. First browser run caught an exact accessible-label mismatch, mobile missing visible H1 and inline link styling; fixed labels, heading structure and underline. A settings Field helper attempted to clone multiple child elements as one React element, triggering the error boundary; mapped/cloned only input/select elements and reran full journeys. Error selectors were narrowed to product alerts rather than Next.js's route announcer. Browser service log was moved outside cleaned test-results to avoid Windows open-file cleanup delays. Final runs pass; failures are not counted as success evidence.

## Security, data and limits

HttpOnly cookie remains unreadable by application JS; central client uses credentials and obtains session-bound CSRF token per mutation. FastAPI validates Origin and ownership; server-only profile fetch forwards only the session cookie, never secret environment values. API_ORIGIN must be set before build and runtime when changing destination. Production still requires same-origin HTTPS proxy, explicit approved HTTPS origins and proper restricted database role; no external deployment claimed.

Browser tests use synthetic accounts and generated databases guarded by TEST_DATABASE_URL=devtreck_test. Runner terminates only its own processes and drops only its generated database. It never clears local development accounts. Service logs/traces/screenshots ignored. No real credentials committed or printed.

Known limits: tested local Windows Chromium only; Safari/Firefox/full browser matrix and hosted Linux CI not yet executed. Automated accessibility and inspected states do not replace a full assistive-technology audit. Client session revalidation has a maximum minute interval while idle, plus immediate checks on focus/navigation/API actions; API authorization always remains authoritative. Theme may apply after hydration; no persistent browser credential storage introduced. Browser task/habit/dashboard screens remain phase 7; focus/progress features are later phases. Password recovery/verification delivery remains deferred.

## Git, manual actions and handover

Branch codex/phase-06. d97f790 adds browser account experience; d9bfa51 adds isolated browser/accessibility tests and CI; final documentation commit records evidence. Main and existing private origin preserved. No push/PR/merge or history rewrite.

No manual setup action required. Production web is running at http://127.0.0.1:3000 with account API at 8002. **Usable now in your browser:** create account, sign in/out, protected overview, edit name/timezone/theme/email/password, and confirm account deletion. **Still usable through API:** tasks/categories, one-time completion/history, daily completions/streaks/reconciliation. Task/habit browser screens arrive in phase 7. Stop here and await that prompt.
