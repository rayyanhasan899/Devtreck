# ADR-0001: Minimal layered monorepo

Status: accepted for authorized phase 1, 2026-11-07.

Use apps/web (Next.js App Router, strict TypeScript, Tailwind) and apps/api (FastAPI, validated Pydantic settings, composition root and thin presentation). Add domain/services/persistence when actual behavior needs them. No empty folders or generic repository framework. SQLAlchemy 2.1 is a stable 2.x dependency; actual persistence and Alembic migrations remain phase 2. Sync database routes are the initial recommendation.

Retain installed Node 24 and Python 3.14 after dependency compatibility checks; exact npm and pip locks make installation reproducible. PostgreSQL 18.6 uses persistent development storage and a separate ephemeral test service, bound to loopback ports 5433/5434 with a required local password. No native PostgreSQL, Kubernetes or Redis needed.

Health reports process liveness only and no configuration/secrets. Production rejects debug and disables schema docs. No permissive CORS. Private-resource authorization arrives with accounts, not a public liveness endpoint. Use portable system fonts to avoid network-dependent font builds.

Alternatives: native database adds machine setup; async ORM is premature without load evidence; microservices add operational cost. Consequences: fewer dependencies to operate; real PostgreSQL constraint/readiness tests and migration history still required in phase 2.

Official sources consulted: [Next.js installation](https://nextjs.org/docs/app/getting-started/installation) (Node minimum 20.9), [FastAPI server](https://fastapi.tiangolo.com/deployment/manually/), [PostgreSQL supported versions](https://www.postgresql.org/support/versioning/). Registry metadata and actual package installation/builds verify exact version compatibility.
