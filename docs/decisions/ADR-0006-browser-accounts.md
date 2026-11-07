# ADR-0006: Same-origin browser accounts

Status: implemented for phase 6, 2026-11-07.

Browser requests use one typed client and relative /api paths. Next.js rewrites proxy to server-only API_ORIGIN (default loopback port 8002), preserving backend session cookies and Origin/CSRF checks. FastAPI remains owner of passwords, sessions, authorization and account transactions. No tokens/passwords are placed in browser persistent storage or public environment variables.

Protected layouts and pages fetch current profile server-side with no-store and HttpOnly cookie forwarding. Missing/invalid sessions redirect to login before private page content is returned. Client checks on navigation, focus and each minute detect revocation while a layout stays mounted. Mutations fetch a fresh session-bound CSRF token. Failed reauthentication is distinguished from expired sessions by checking the current profile; wrong current password does not unnecessarily sign out a valid user.

Profile/name/timezone/theme, reauthenticated email/password changes and confirmed deletion are complete browser workflows. Theme persists in backend preferences; system/light/dark tokens apply to document. Device timezone is a suggestion requiring Save confirmation; no historical record rewriting. Native dialog supplies focus trapping, Escape and focus return for deletion; checkbox and current password required. Only Overview and Settings are linked in authenticated navigation until task screens exist.

Alternatives: direct cross-origin browser API requires more CORS/cookie configuration; moving auth logic into Next duplicates security policy; browser token storage exposes credentials to scripts. Consequences: production must route API and web under one origin and configure HTTPS/approved origins. API_ORIGIN must be set before build for rewrite destinations and at server runtime for protected profile fetches.

Playwright browser journeys run against a generated disposable database and temporary ports 8010/3100. The runner owns and cleans its processes/database; valuable local accounts are untouched. Chromium and axe checks complement API tests; they do not claim all-browser or full-product accessibility.
