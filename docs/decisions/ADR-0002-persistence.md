# ADR-0002: Explicit synchronous transactions and safe persistence boundary

Status: accepted for phase 2, 2026-11-07.

Use SQLAlchemy 2.1 synchronous engines and sync DB route handlers. Each request receives its own session; dependency cleanup always rolls back uncommitted changes and closes it. Explicit SqlUnitOfWork commit is the application boundary and rolls back failures. Repositories never commit. Repository port returns framework-free domain User, not ORM/Pydantic. Caller owns UoW session lifetime; production account workflows will consume these contracts in phase 3.

Composition creates/disposes engine during lifespan; pre-ping, bounded pool and connection timeout handle stale/unavailable connections. Configuration stores DSN as SecretStr and hides validation inputs. SQLAlchemy hides bound parameters; application logs never stringify DB exceptions. Production configuration requires PostgreSQL psycopg URL.

Initial migration supplies user/session tables without exposing auth routes. Database token hashes are foundations, not an authentication implementation. Ownership FK cascade is essential; later task relationships require owner-aware composite constraints or explicit application authorization. IANA timezone/history policy remains proposed until streak implementation.

Alternatives: async would require consistent async application/repository boundaries and is not justified by current scale; per-repository commit breaks atomic workflows; create_all cannot represent schema history; SQLite cannot verify PostgreSQL constraints and concurrency. Consequences: explicit session ownership and migration discipline; disposable integration test role requires CREATEDB. Do not grant that permission to production app role.

References: https://docs.sqlalchemy.org/en/21/orm/session_basics.html and https://alembic.sqlalchemy.org/en/latest/tutorial.html (checked during phase 2). No package upgrade required.
