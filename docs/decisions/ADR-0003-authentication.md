# ADR-0003: Revocable cookies and reauthenticated account lifecycle

Status: implemented under authorized phase 3 prompt, 2026-11-07.

Choose server-side opaque cookie sessions (seven-day absolute duration), SHA-256 token digests in DB and Argon2id password hashes. Argon2-cffi recommended default m=65536,t=3,p=4; password 12–128 Unicode characters without forced composition. Registration returns profile, followed by explicit login. Production cookies require HTTPS; SameSite Strict plus exact Origin checks and session-bound CSRF header protect mutations. Session token entropy supports an unkeyed session-token digest; CSRF token is derived from the random opaque cookie and available only through authenticated no-store responses. Never put credentials in browser localStorage.

Current password is required for password change, email change and confirmed account deletion. Email/password changes revoke all sessions; logout revokes only current. Row locking refreshes account values before checking password and serializes account changes/session issuance. Constraints enforce normalized email, nonblank name and allowed theme; IANA validation is application-side. Account deletion cascades all current user/session rows; extend policy in later schemas.

Database fixed-window throttling commits attempt counters independently of account transaction, preventing rollback of failed attempt counts. Atomic upsert supports multiple API processes. No forwarded header trust until a trusted proxy strategy is configured. Rate metadata retains only hashed keys and short windows, removed opportunistically; no raw personal values. Current direct persistence adapter is account-specific, not a generic repository framework; domain contains no FastAPI/SQLAlchemy dependencies. Transport exceptions mapped at presentation.

Alternatives: browser bearer-token storage increases exposure; JWT-only revocation complicates password/account deletion; Redis introduces another service. Consequences: server lookup per request, CSRF-aware client and same-origin production routing. No password recovery or verification email until real delivery is scoped.

Compatibility: argon2-cffi 25.1.0 and email-validator 2.3.0 installed/pinned; official Argon2 how-to checked: https://argon2-cffi.readthedocs.io/en/stable/howto.html. Dependencies verified through actual installs, imports and tests.

Update2026-11-08: the user explicitly approved committing their8-character minimum edits. Current API and browser registration/password-change policy is8–128characters; all other authentication decisions above remain unchanged.
