# Accounts API (phase 3)

Run from apps/api: `.venv/Scripts/python -m uvicorn app.main:app --host 127.0.0.1 --port 8002 --no-access-log`. Inspect http://127.0.0.1:8002/docs. This is an API release; web account screens arrive in phase 6.

All mutation requests require Origin matching ALLOWED_ORIGINS. Development defaults: http://localhost:3000, http://127.0.0.1:3000 and http://127.0.0.1:8002. ALLOWED_ORIGINS is a JSON array of exact HTTP(S) origins; production requires explicit HTTPS values. No permissive CORS, no forwarded-IP trust. Production proxy must route frontend and API on the same origin and terminate HTTPS. Use --no-access-log to avoid logging query strings.

| Endpoint | Body/behavior |
|---|---|
| POST /api/auth/register | name, email, password; returns profile 201; then login |
| POST /api/auth/login | email, password; profile and csrf_token; sets HttpOnly session cookie |
| GET /api/auth/csrf | authenticated, returns session-bound csrf_token after refresh |
| POST /api/auth/logout | X-CSRF-Token; revokes current session and clears cookie; 204 |
| GET /api/users/me | current authenticated profile only |
| PATCH /api/users/me | optional name/email/time_zone/theme; email also requires current_password; email change revokes all sessions |
| PATCH /api/users/me/password | current_password, new_password; revokes all sessions; 204 |
| DELETE /api/users/me | current_password and confirm:true; deletes account and all existing owned sessions; 204 |

Authenticated mutations require X-CSRF-Token from login/csrf response AND session cookie AND approved Origin. API clients must keep cookie jar. Use real credentials only in local secure tools, not chat or committed examples. /docs can exercise registration/login; copy returned CSRF token into your API client for protected mutations. The token is session-specific; never publish it.

Passwords: 8–128 characters for registration/change, reflecting the user's password-policy edits approved for commit on 2026-11-08; no trimming or forced composition, Unicode supported. Names trimmed, 1–120 characters. Emails validated and trim/lowercase normalized; unique DB constraint handles concurrent registration. IANA zones checked using zoneinfo; theme light/dark/system. Unknown fields (including user_id/id) rejected; omitted/null profile fields preserve current values. Notification channels/recovery are not implemented and no delivery is claimed.

Session: cryptographically random 32-byte opaque value; SHA-256 digest only in PostgreSQL; HttpOnly, SameSite=Strict, path=/, seven-day absolute expiration; Secure in production. No sliding extension. Password/email change revokes all sessions, including current; log in again. Password verification uses Argon2id (64 MiB, 3 iterations, parallelism 4), rehashes on login as required. Missing/wrong credentials return the same safe 401; unknown emails still run a dummy Argon2 verification.

Sensitive routes use atomic PostgreSQL fixed ten-minute-window counters. Registration 10/IP, login 20/IP and 10/normalized-email, password/delete 10/IP, profile 30/IP, logout 60/IP. Scope/IP/email keys are SHA-256 digests; no raw email/IP in table. Stale windows older than the preceding window are cleaned on sensitive requests; account deletion also removes its email throttle key. Database maintenance can purge expired sessions/stale counters periodically. Fixed-window rate limits allow boundary bursts and account throttles can temporarily affect legitimate users; no Redis infrastructure needed. Production app role must not use local/CI superuser privileges.

Profiles never include password or session hashes. Responses use Cache-Control:no-store. Private profile routes accept no arbitrary account ID; another ID path is unavailable. Safe validation errors identify allowlisted field names without echoing submitted input. Cookies are revoked server-side, not merely removed in browser. Account deletion covers current schema; each future owned table must join documented cascade/privacy policy.
