# Persistence and migrations

User/session foundations are in migration 496d77b4d913. UUID keys, normalized trimmed/lowercase unique email, password hash only, IANA timezone preference (UTC default), theme (system default), timezone-aware created/updated timestamps. Sessions hold unique token hashes, owner FK with cascade, created/expiry timestamps and positive lifetime check; owner and expiry indexed. Actual authentication, Argon2 hashing, expiry enforcement and full profile validation remain phase 3.

Database owns email uniqueness and referential integrity; application normalizes input and validates IANA zone/theme in account workflows. UTC connection option is set for request engine. updated_at changes through SQLAlchemy updates, not arbitrary direct SQL; future application writes use repositories. No task tables exist yet. Future child records must have owner FKs; cross-resource links must enforce matching owners via composite constraints or transactional ownership queries, never a client owner ID.

## Local configuration

Root .env configures Compose only. apps/api/.env configures DATABASE_URL; apps/api/.env.test configures TEST_DATABASE_URL. Examples are in root .env.example. Substitute the root local database password securely, URL-encode reserved characters, never print or commit it. Existing local files were generated directly without exposing values. Production requires DATABASE_URL. Debug is forbidden in production; absent database config in development allows liveness but readiness returns 503.

From apps/api with venv Python:

```powershell
.venv/Scripts/python -m alembic upgrade head
.venv/Scripts/python -m alembic current
.venv/Scripts/python -m alembic check
```

Apply development migration only when intended; this phase tested round-trips on disposable random databases, then applied the verified additive initial migration to the local development database. Do not run downgrade on valuable data. Review autogenerate output before committing; use explicit schema changes and reproducible revision history. No create_all startup or automatic production migration.

## Verification safety

Run pytest from apps/api. TEST_DATABASE_URL must name devtreck_test and use a local/CI role with CREATEDB privilege. Tests create a random devtreck_verify_<uuid> database through that connection and drop only that generated database in teardown. Existing development and test database contents are never reset. Tests skip integration checks only when no test URL is supplied; a skipped suite is not phase acceptance. CI supplies PostgreSQL and a disposable URL explicitly.

Tests cover upgrade/base/head/check, transactional DDL rollback, UoW commit/rollback/failed-commit recovery, concurrent unique-email writes, normalized email checks, cascade/FK, timestamp timezone, request-session cleanup and readiness success/outage. Application tests run against real PostgreSQL, not SQLite. The DDL rollback test simulates failure inside a PostgreSQL transaction; it is not a production rollback drill.

## Phase 9 additions

Revision `8022c27c58ae` adds xp_ledger (unique owner/source keys and nonnegative amounts), achievements (owner/key primary key), eligible_occurrences (owner/task composite cascade, daily uniqueness and partial one-time uniqueness), and insight_days (owner/date coverage). Owner/day indexes support lookups. All tables cascade on account deletion; XP deliberately has no task FK. Applied additive upgrade/check to local development; disposable test suite performs downgrade/base/head round trips and metadata agreement. [Retention and denominator contract](../api/progress.md).
