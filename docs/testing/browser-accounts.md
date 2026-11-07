# Browser account checks

Install locked web dependencies, API dependencies and Chromium:

```powershell
npm ci --prefix apps/web
```

From apps/web run `npx playwright install chromium`. With Docker test service healthy and apps/api/.env.test TEST_DATABASE_URL naming devtreck_test, run from repository root:

```powershell
apps/api/.venv/Scripts/python apps/api/scripts/browser_checks.py
```

The runner creates devtreck_browser_<uuid> through the separate test service, migrates it, starts API 8010 and web 3100, runs three browser journeys, then stops only its owned processes and drops only that random database. Test role needs CREATEDB; never use production role or database. Reuse of existing servers is intentionally disabled. Windows/Linux cleanup paths supported; Linux hosted execution is separate from local results.

Checks cover registration/login, profile/name/timezone/theme persistence, email/password reauthentication and session revocation, deletion dialog/Escape/confirmation, protected navigation, explicit server-side logout replay detection, keyboard/mobile layout, failed save rollback after network error and automated accessibility. API tests separately prove actual seven-day expiration behavior. No screenshot/trace contains real user credentials; all records are disposable synthetic test accounts.

Screenshots/traces are ignored in apps/web/test-results; service output is in ignored apps/web/.browser-services.log, outside Playwright's cleaned output directory to avoid Windows file-lock delays. Do not commit logs or sensitive browser state. CI has a dedicated PostgreSQL/browser job with failure artifacts. Build/lint/type checks remain separate gates. No task/habit UI is claimed by these tests.
