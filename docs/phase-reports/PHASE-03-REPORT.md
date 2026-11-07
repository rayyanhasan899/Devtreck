# Phase 03 report — Accounts and authentication

2026-11-07, Asia/Karachi. Status: **PASS WITH KNOWN LIMITATIONS**.

## Objective and actual features

Complete phase 3 API account lifecycle: registration followed by login; logout; protected current profile; update name/email/IANA timezone/theme; current-password-protected password/email changes; confirmed, reauthenticated account deletion. Password/email change revokes every account session. Account deletion removes user/sessions and account email throttle key. Future owned tables must extend cascading deletion policy.

Opaque seven-day sessions use random 32-byte token, SHA-256 digest only in DB, HttpOnly/SameSite Strict cookie and production Secure flag. Mutations require exact approved Origin and authenticated mutations also require session-bound CSRF header. GET csrf supports refresh. Passwords use Argon2id recommended parameters, dummy verify for unknown email and rehash-on-login. Database-backed atomic fixed-window limits protect registration/login/profile/password/deletion/logout. Account row locking refreshes before password checks and serializes credential changes. All API responses are no-store; logs and errors omit credentials. Safe validation field paths added without echoing values.

## Requirements and traceability

ACC-01–07 registration: schemas/service/unique normalized email; validation/normalization/hash tests. ACC-08–14 login/logout/protected/session/config: account routes/service/security/repository; expiry, replay, generic login, cookie and throttle tests. ACC-15–18 profile/email/password: current-profile routes plus reauthentication; timezone/theme/email conflict/password tests. ACC-19–21 deletion/privacy: DELETE me confirmation, current password and FK cascade; two-user separation/ID injection/deletion tests. SEC-01–04/06–07/10/12–14 apply to these account resources; SEC-05/08–09/11 reuse validated secrets, no permissive CORS, HTTPS production origins and safe logs. Other feature resources do not exist yet, so future authorization is not claimed. Requirements 16.1 account acceptance is covered at API level; browser UI remains phase 6.

## Changed files and decisions

Added core/security.py, account schemas/routes, account persistence adapter/service and test_accounts.py. Modified config, errors, composition root, models, foundation tests and pinned Python dependency definitions/lock. Added migration 73e8369b569c: rate_limits table/window index, user theme and nonblank name constraints. No files deleted. Updated README/Assumptions; added account API guide and ADR-0003. No frontend source changes.

ADR-0003 documents session duration, hashing, CSRF, password policy, reauthentication, normalization and throttling. A-01/A-17/A-19 progressed under explicit phase authorization; A-21–24 record recommended implementation defaults. Password policy 12–128 Unicode characters; no trimming/composition requirement. Notification channels/recovery remain unimplemented optional scope; timezone history behavior remains phase 5.

## Tools and verification

Existing Python 3.14.7/SQLAlchemy 2.1.8/Alembic 1.20.1/psycopg 3.3.8/PostgreSQL 18.6/Node 24 retained. Added argon2-cffi 25.1.0, email-validator 2.3.0 and pinned transitive packages. Official Argon2 how-to checked. Existing verification venv installed updated lock successfully and pip check passed.

From apps/api: Ruff lint passed; Ruff format check passed (29 files); mypy passed (26 source files); pytest **23 passed**, no warnings/skips. Tests include normalized duplicates, unknown fields/invalid name/email/password, Argon2 storage, no hash response, login expiry/logout replay, missing/wrong CSRF and Origin, two-user privacy, ID substitution, IANA validation, profile preferences, duplicate email conflict, email reauthentication/revocation, wrong-current-password rejection, password-change all-session revocation, confirmed deletion/cascade, generic failures, rate-limit enforcement, Secure/HttpOnly/SameSite cookie flags, no-store, concurrent registration and atomic counters. Prior persistence/config/readiness/migration/redaction tests remain passing.

Disposable PostgreSQL fixture exercised base→head→base→head including the new revision and alembic check with no drift; existing test/development data was never reset. After tests, local development alembic upgrade head/current/check passed at 73e8369b569c. Future production migrations require explicit approval.

From apps/web: npm run lint, typecheck and build passed unchanged. Updated Uvicorn launched on 127.0.0.1:8002 with --no-access-log; live /ready and /docs returned HTTP 200. git diff --check passed before commits. No GitHub CI run, push, PR or deployment claimed.

## Failures and fixes

Initial strict typing found an insert-returning statement variable type and missing route helper annotation; fixed. Ruff found imports/fixture-name warnings and formatting; corrected and final checks passed. Database name/theme constraints and stale throttle cleanup were added before final migration verification. No unresolved test failure.

## Limitations and security/data notes

No browser account forms yet; use API tools. Recovery/email verification/notification delivery are deferred; email change requires current password and uniqueness but does not claim verified mailbox ownership. Production needs HTTPS, explicit allowed origins, same-origin proxy and correct limited database role. Development cookie intentionally omits Secure for loopback HTTP. Fixed-window limits permit boundary bursts and shared-IP/account throttles can temporarily affect legitimate users; no forwarded-IP trust. Stale rate windows cleaned opportunistically; expired sessions are rejected, with periodic purge recommended. Rate keys are hashed rather than plaintext; deletion removes the account email throttle key. Only current schema data can be tested for deletion; future tables must extend it.

Public health is not authentication; API routes require session checks. User password hashes/tokens never appear in profile responses. Root/API-local ignored credential files remain private. Test accounts exist only in generated disposable databases removed by fixtures; no demo account or fixed credential was introduced. Production debugging/docs exposure remains disabled. Hosted CI and full browser E2E remain unrun in this phase.

## Git and handover

Branch codex/phase-03 from verified phase 2. Focused commits: secure lifecycle implementation, account security/concurrency tests, and documentation/report. Exact hashes in git log. Main/private origin unchanged; no pushes, merges, resets or history rewriting. No manual action required. Updated API is left running on 8002; older API processes on 8000/8001 may still serve old code and should not be used for account testing.

**Available now:** welcome web page plus API registration, login/logout, private profile, timezone/theme/email/password updates and confirmed account deletion. API documentation: http://127.0.0.1:8002/docs; detailed cookie/CSRF usage: docs/api/accounts.md. Task management, habits, focus and account browser screens are not available yet. Phase 3 local exit criteria met; stop and await phase 4 prompt.
