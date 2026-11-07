# Devtreck — Architecture & Project Management Blueprint

> **Purpose:** A reusable architectural skeleton for Devtreck and future projects built with **Next.js + TypeScript + Tailwind CSS + Python + FastAPI + PostgreSQL + SQLAlchemy**.
>
> **Architectural style:** Layered Architecture with explicit dependency direction.
>
> **Primary goal:** Keep the codebase **manageable, scalable, clean, traceable, testable, and predictable** as the project grows.

---

## 1. Architectural Objective

This project follows a five-layer model:

1. **Presentation Layer** — UI, HTTP/API controllers, request/response handling.
2. **Service Layer** — Application services, use cases, orchestration, transactions.
3. **Domain Layer** — Business entities, value objects, business rules, domain logic.
4. **Persistence Layer** — Repositories, DAOs, ORM mappings, database access implementation.
5. **Database Layer** — PostgreSQL itself: schemas, tables, indexes, constraints, extensions, and physical storage.

The important idea is that each layer has a clear responsibility and a controlled relationship with the other layers.

### Dependency direction

The preferred direction is:

```text
Presentation
     ↓
Service / Application
     ↓
Domain
     ↑
Persistence
     ↓
Database
```

More precisely, the **Domain should not depend on infrastructure**. Persistence implements interfaces/contracts required by the Service/Domain side. Presentation depends on application-facing contracts, not directly on database code.

A useful mental model is:

```text
                ┌───────────────────────────┐
                │      Presentation         │
                │ Next.js / FastAPI routes  │
                └─────────────┬─────────────┘
                              │
                              ▼
                ┌───────────────────────────┐
                │     Service / App         │
                │   Use Cases / Workflows   │
                └─────────────┬─────────────┘
                              │
                              ▼
                ┌───────────────────────────┐
                │          Domain           │
                │ Rules / Entities / VOs     │
                └─────────────▲─────────────┘
                              │
                ┌─────────────┴─────────────┐
                │        Persistence        │
                │ Repositories / SQLAlchemy │
                └─────────────┬─────────────┘
                              │
                              ▼
                ┌───────────────────────────┐
                │         PostgreSQL        │
                │ Schema / Tables / Indexes │
                └───────────────────────────┘
```

> **Key principle:** A layer should not reach around the layer immediately responsible for the concern it needs.

---

# 2. Recommended Repository Structure

For a full-stack monorepo, use a clear top-level split between frontend and backend.

```text
devtreck/
│
├── apps/
│   ├── web/                         # Next.js frontend
│   │   ├── public/
│   │   └── src/
│   │       ├── app/                # Next.js App Router
│   │       ├── components/         # Reusable UI components
│   │       ├── features/           # Feature-specific presentation logic
│   │       ├── hooks/              # React/client hooks
│   │       ├── lib/                # Frontend utilities/configuration
│   │       ├── services/           # Frontend API client layer
│   │       ├── types/              # Frontend-only types
│   │       └── styles/             # Global styles / Tailwind support
│   │
│   └── api/                        # FastAPI backend
│       ├── app/
│       │   ├── presentation/
│       │   ├── services/
│       │   ├── domain/
│       │   ├── persistence/
│       │   ├── database/
│       │   ├── core/
│       │   └── main.py
│       │
│       └── tests/
│
├── packages/
│   ├── contracts/                  # Optional shared API/schema concepts
│   └── config/                     # Optional shared tooling/config
│
├── infra/                          # Deployment/infrastructure definitions
│   ├── docker/
│   ├── nginx/
│   └── scripts/
│
├── docs/                           # Architecture and project documentation
│   ├── architecture/
│   ├── api/
│   ├── database/
│   └── decisions/
│
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Makefile / justfile             # Optional project command shortcuts
└── README.md
```

This is intentionally a **generic skeleton**. It is not specific to Devtreck's business functionality and can be reused as a starting point for other products.

---

# 3. Backend Structure in Detail

Recommended FastAPI layout:

```text
apps/api/
│
├── app/
│   ├── main.py
│   │
│   ├── presentation/
│   │   ├── api/
│   │   │   ├── v1/
│   │   │   │   ├── router.py
│   │   │   │   ├── endpoints/
│   │   │   │   │   ├── users.py
│   │   │   │   │   ├── projects.py
│   │   │   │   │   └── ...
│   │   │   │   └── dependencies.py
│   │   │   └── router.py
│   │   │
│   │   ├── schemas/                # Pydantic request/response models
│   │   ├── controllers/            # Optional if controllers need abstraction
│   │   └── exception_handlers.py
│   │
│   ├── services/
│   │   ├── interfaces/
│   │   │   └── repositories/
│   │   ├── use_cases/
│   │   ├── application_services/
│   │   └── dto/
│   │
│   ├── domain/
│   │   ├── entities/
│   │   ├── value_objects/
│   │   ├── services/
│   │   ├── events/
│   │   ├── exceptions.py
│   │   └── enums.py
│   │
│   ├── persistence/
│   │   ├── models/                 # SQLAlchemy ORM models
│   │   ├── repositories/           # Concrete repository implementations
│   │   ├── queries/
│   │   ├── mappers/
│   │   └── unit_of_work.py
│   │
│   ├── database/
│   │   ├── session.py              # Engine/session factory
│   │   ├── base.py                 # Declarative base/metadata
│   │   ├── migrations/
│   │   └── seed/
│   │
│   ├── core/
│   │   ├── config.py               # Environment/settings
│   │   ├── security.py
│   │   ├── logging.py
│   │   ├── errors.py
│   │   └── dependencies.py
│   │
│   └── main.py
│
└── tests/
    ├── unit/
    ├── integration/
    └── e2e/
```

The exact feature names should change from project to project. The architectural roles should remain stable.

---

# 4. Presentation Layer

## Responsibility

The Presentation Layer handles communication with users and external clients.

For the backend, this generally means:

- FastAPI routes/endpoints
- HTTP methods and status codes
- Authentication/authorization entry points
- Request validation
- Response serialization
- API versioning
- Mapping application errors to HTTP responses

For the frontend, this means:

- Next.js pages and layouts
- React components
- Forms
- Loading/error states
- Client-side interaction
- UI-specific state
- Calling backend APIs through a controlled client layer

## What belongs here

```text
presentation/
├── api/
│   ├── v1/
│   │   ├── endpoints/
│   │   └── router.py
│   └── dependencies.py
├── schemas/
└── exception_handlers.py
```

### Do

```python
@router.post("/projects")
async def create_project(
    payload: CreateProjectRequest,
    service: ProjectService = Depends(get_project_service),
):
    result = await service.create_project(payload)
    return ProjectResponse.from_result(result)
```

### Do not

```python
@router.post("/projects")
async def create_project(payload: dict, db: Session = Depends(get_db)):
    # Business rules + SQLAlchemy queries + response formatting
    # all in one route
    ...
```

Routes should be thin. They should translate transport-level input into an application call and translate the result into a transport-level response.

---

# 5. Service Layer

## Responsibility

The Service Layer coordinates application behavior.

It answers questions such as:

> "What steps must occur when this application operation is executed?"

Typical responsibilities:

- Use cases
- Application workflows
- Orchestration between domain objects
- Transaction boundaries
- Calling repositories
- Calling external infrastructure through abstractions
- Authorization decisions at the application-operation level
- Mapping input DTOs into domain operations
- Returning application results

Example:

```text
CreateProjectUseCase
    │
    ├── validate application-level preconditions
    ├── create domain entity
    ├── repository.save(entity)
    ├── commit transaction
    └── return result DTO
```

The Service Layer should **not become a second domain layer**. Business rules that define what is inherently valid should live in the Domain whenever practical.

---

# 6. Domain Layer

The Domain is the architectural center of the backend.

It contains business concepts independently of FastAPI, SQLAlchemy, PostgreSQL, HTTP, React, or Next.js.

## Typical contents

```text
domain/
├── entities/
├── value_objects/
├── services/
├── events/
├── enums.py
└── exceptions.py
```

## Entities

Objects with identity and a lifecycle.

```python
class Project:
    def __init__(self, project_id, name):
        self.id = project_id
        self.name = name

    def rename(self, new_name: str) -> None:
        if not new_name.strip():
            raise DomainError("Project name cannot be empty")
        self.name = new_name.strip()
```

The example is deliberately framework-independent.

## Value Objects

Value objects represent concepts whose identity is defined by their values.

Examples:

- EmailAddress
- Money
- DateRange
- ProjectSlug
- Percentage
- Coordinates

Example:

```python
@dataclass(frozen=True)
class EmailAddress:
    value: str

    def __post_init__(self):
        if "@" not in self.value:
            raise ValueError("Invalid email address")
```

## Domain Services

Use a domain service when a business rule:

- is genuinely domain logic,
- does not naturally belong to one entity/value object, and
- is still independent of infrastructure.

Do not create a domain service merely because a function contains more than a few lines.

---

# 7. Persistence Layer

The Persistence Layer is where application/domain concepts are translated to storage operations.

Typical contents:

```text
persistence/
├── models/
├── repositories/
├── queries/
├── mappers/
└── unit_of_work.py
```

## SQLAlchemy ORM models

SQLAlchemy models represent the persistence representation of data.

Example:

```python
class ProjectModel(Base):
    __tablename__ = "projects"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
```

These models are infrastructure concerns. Avoid making your domain model depend on SQLAlchemy unless there is a deliberate architectural reason to do so.

## Repositories

The repository abstraction describes what the application needs from persistence.

Example contract:

```python
class ProjectRepository(Protocol):
    async def get_by_id(self, project_id: UUID) -> Project | None: ...
    async def add(self, project: Project) -> None: ...
    async def delete(self, project_id: UUID) -> None: ...
```

The SQLAlchemy implementation lives in Persistence:

```text
services/interfaces/repositories/project_repository.py
                     ▲
                     │ implemented by
                     │
persistence/repositories/sqlalchemy_project_repository.py
```

This prevents business logic from needing to know how PostgreSQL is queried.

---

# 8. Database Layer

The Database Layer is PostgreSQL itself plus database-specific structural concerns.

It includes:

- Tables
- Columns
- Primary keys
- Foreign keys
- Unique constraints
- Check constraints
- Indexes
- Sequences/identity configuration
- PostgreSQL extensions when needed
- Database roles/permissions
- Physical storage configuration
- Migration history

Keep the distinction clear:

```text
Database Layer
    = PostgreSQL structure and storage

Persistence Layer
    = Python code that communicates with PostgreSQL
```

---

# 9. Database Migrations

Use a migration tool such as **Alembic** with SQLAlchemy.

Recommended structure:

```text
app/database/migrations/
├── env.py
├── script.py.mako
└── versions/
    ├── 0001_initial_schema.py
    ├── 0002_add_project_indexes.py
    └── ...
```

Migration rules:

1. Every schema change must be represented by a migration.
2. Never rely on manually changing production tables.
3. Keep migrations ordered and reproducible.
4. Review generated migrations before applying them.
5. Keep destructive changes deliberate and separately reviewed.
6. Test both upgrade and downgrade paths where your operational process requires downgrades.

The ORM model defines the intended application-side representation; migrations define the historical changes to the physical database.

---

# 10. Frontend Architecture

The Next.js application should also have boundaries, even though the five-layer backend model is most useful on the server.

Recommended frontend layout:

```text
apps/web/src/
│
├── app/                            # Routes, layouts, loading/error boundaries
│
├── components/
│   ├── ui/                         # Generic UI primitives
│   └── shared/                     # Cross-feature components
│
├── features/
│   ├── feature-a/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── api.ts
│   │   ├── types.ts
│   │   └── utils.ts
│   └── feature-b/
│
├── services/
│   ├── api-client.ts               # HTTP client setup
│   ├── auth.ts                     # Frontend auth integration
│   └── endpoints/
│
├── lib/
│   ├── env.ts
│   ├── dates.ts
│   └── utils.ts
│
├── hooks/
└── types/
```

### Recommended frontend flow

```text
Page / Component
      ↓
Feature Hook / Action
      ↓
Frontend API Client
      ↓
FastAPI Endpoint
      ↓
Application Service / Use Case
```

Do not make arbitrary components issue raw `fetch()` calls against different URLs throughout the codebase. Centralize API communication.

---

# 11. API Contract Boundary

The frontend and backend should communicate through explicit API contracts.

A useful boundary is:

```text
Next.js Types / Generated Client
              ↕
         HTTP + JSON
              ↕
FastAPI Pydantic Schemas
```

Recommended backend schemas:

```text
presentation/schemas/
├── common.py
├── project.py
├── user.py
└── error.py
```

Do not expose SQLAlchemy models directly as your long-term API contract.

A database model is shaped around storage. An API schema is shaped around communication.

Those concerns can evolve independently.

---

# 12. Pydantic vs Domain Models vs SQLAlchemy Models

Keep these three concepts distinct.

| Model | Primary Purpose | Layer |
|---|---|---|
| Pydantic schema | Validate/serialize API data | Presentation |
| Domain entity/value object | Represent business concepts/rules | Domain |
| SQLAlchemy model | Represent database persistence | Persistence |

For example:

```text
CreateProjectRequest
        ↓
CreateProjectUseCase
        ↓
Project (Domain Entity)
        ↓
ProjectRepository
        ↓
ProjectModel (SQLAlchemy)
        ↓
PostgreSQL
```

This separation dramatically improves traceability when requirements or storage structure change.

---

# 13. Dependency Injection

Use dependency injection to wire infrastructure into application services.

The Presentation Layer may depend on a dependency provider:

```python
def get_project_service() -> ProjectService:
    repository = get_project_repository()
    return ProjectService(repository)
```

FastAPI's dependency system is useful for this boundary.

However, do not allow dependency injection to become a hidden global service locator. Prefer explicit constructor dependencies inside application/domain code.

---

# 14. Unit of Work and Transactions

Transactions should have a clear boundary.

A common pattern is:

```text
HTTP Request
    ↓
Use Case
    ↓
Unit of Work
    ├── Repository A
    ├── Repository B
    └── Repository C
    ↓
Commit / Rollback
```

The key question is:

> Which complete application operation must succeed or fail as one unit?

That operation should usually define the transaction boundary.

Avoid committing inside every individual repository method unless there is a deliberate reason.

---

# 15. Error Handling Strategy

Define error categories.

```text
Domain Errors
    ↓
Application Errors
    ↓
Presentation Mapping
    ↓
HTTP Response
```

For example:

```text
DomainError
NotFoundError
ConflictError
ValidationError
AuthorizationError
InfrastructureError
```

The domain should not raise `HTTPException`.

Bad:

```python
raise HTTPException(status_code=400, detail="Invalid project")
```

Better:

```python
raise InvalidProjectError("Project cannot be activated")
```

Then map the domain/application error to HTTP at the Presentation Layer.

---

# 16. Authentication and Authorization Placement

Keep responsibilities separated.

```text
Authentication
    = Who is this caller?

Authorization
    = Is this caller allowed to perform this operation?
```

Recommended split:

- Token/session parsing: Presentation/Core infrastructure.
- User identity object/context: application boundary.
- Operation-level permission checks: Service/Application layer.
- Resource-specific business invariants: Domain layer.
- Password/token persistence: Persistence/Infrastructure.

Do not bury authorization decisions inside random UI components or SQLAlchemy models.

---

# 17. Configuration and Environment Management

Use environment-specific configuration rather than hardcoding infrastructure settings.

Example:

```text
.env.example

APP_ENV=development
APP_DEBUG=true
DATABASE_URL=postgresql+asyncpg://...
JWT_SECRET=change-me
API_BASE_URL=http://localhost:8000
```

Recommended rules:

- Commit `.env.example`.
- Do not commit real secrets.
- Validate configuration at startup.
- Keep environment-specific values outside business logic.
- Centralize backend settings in `core/config.py`.
- Centralize frontend environment access in a small configuration module.

---

# 18. Logging and Observability

Use structured logging where possible.

Each request should ideally be traceable using a request/correlation ID.

Useful metadata includes:

```text
request_id
user_id (when appropriate and safe)
route
HTTP method
status code
duration
service/use-case name
error category
```

Do not log:

- Passwords
- Access tokens
- Secret keys
- Sensitive request bodies without a clear need
- Database credentials

A scalable application should make it possible to answer:

> "A user reported a failure. Which request reached which endpoint, which use case executed, and what persistence operation failed?"

---

# 19. Testing Architecture

Organize tests by architectural boundary.

```text
tests/
├── unit/
│   ├── domain/
│   └── services/
│
├── integration/
│   ├── persistence/
│   ├── database/
│   └── api/
│
└── e2e/
    └── workflows/
```

### Unit tests

Fast and isolated.

Test:

- Domain rules
- Value objects
- Application services/use cases
- Error conditions

Mock repository interfaces rather than SQLAlchemy internals where practical.

### Integration tests

Test real boundaries:

- SQLAlchemy ↔ PostgreSQL
- Repository implementations
- FastAPI ↔ application services
- Authentication infrastructure

### E2E tests

Test complete user workflows through the actual frontend/backend path.

Do not use E2E tests for every small business rule. Keep detailed rules in lower-level tests.

---

# 20. Dependency Rules

The following rules should be treated as architectural guardrails.

## Rule 1 — Presentation does not contain business logic

Routes and React components should coordinate and display/transport information.

## Rule 2 — Domain does not depend on infrastructure

Avoid imports such as:

```python
from fastapi import HTTPException
from sqlalchemy.orm import Session
```

inside core domain objects.

## Rule 3 — Services do not write SQL directly

Application services should use repositories/ports rather than issuing SQLAlchemy queries themselves.

## Rule 4 — Persistence implements abstractions

Database details stay behind repository implementations and persistence services.

## Rule 5 — Database models are not API contracts

Serialize through Pydantic response schemas.

## Rule 6 — Frontend does not know PostgreSQL exists

The browser/client should know only the API contract.

## Rule 7 — Cross-layer imports must be intentional

Avoid a situation where any file can import any other file.

---

# 21. Dependency Matrix

A simple project-wide rule set:

| Layer | May Depend On | Should Not Depend Directly On |
|---|---|---|
| Presentation | Services, contracts, presentation utilities | SQLAlchemy queries, PostgreSQL details |
| Service | Domain, repository interfaces, application abstractions | FastAPI transport details, React, PostgreSQL directly |
| Domain | Standard library, domain code | FastAPI, SQLAlchemy, PostgreSQL |
| Persistence | Domain, repository contracts, SQLAlchemy | React/Next.js |
| Database | PostgreSQL infrastructure | UI/Application code |

The exact implementation can evolve, but the **direction of coupling should remain deliberate**.

---

# 22. Feature-Based Organization Inside Layers

As the application grows, a purely technical folder structure can become difficult to navigate.

A scalable approach is to combine **layering + feature boundaries**.

Example:

```text
app/
├── presentation/
│   └── api/v1/endpoints/
│       ├── projects.py
│       └── users.py
│
├── services/
│   └── projects/
│       ├── create_project.py
│       ├── update_project.py
│       └── delete_project.py
│
├── domain/
│   └── projects/
│       ├── entities.py
│       ├── value_objects.py
│       └── exceptions.py
│
└── persistence/
    └── projects/
        ├── models.py
        ├── repository.py
        └── queries.py
```

This makes tracing a feature easier:

```text
Project API
 → CreateProjectUseCase
 → Project Domain
 → ProjectRepository
 → ProjectModel
 → PostgreSQL
```

For larger systems, this hybrid structure is usually easier to navigate than one giant folder containing every application's services/entities/repositories.

---

# 23. Naming Conventions

Use predictable names.

## Python

```text
snake_case.py
PascalCase              # Classes
snake_case              # functions/variables
UPPER_SNAKE_CASE        # constants
```

Examples:

```text
project_repository.py
create_project.py
project_service.py
```

## TypeScript

Use a consistent convention such as:

```text
kebab-case.ts / kebab-case.tsx
PascalCase                 # React components/types/classes
camelCase                  # functions/variables
UPPER_SNAKE_CASE           # constants when appropriate
```

The exact convention matters less than consistency.

---

# 24. API Versioning

Start with explicit versioning for public or long-lived APIs when appropriate:

```text
/api/v1/...
```

Version when the contract meaningfully changes, not merely for every deployment.

Do not create `v2` folders simply because the codebase became messy. Versioning is for API compatibility boundaries, not internal refactoring.

---

# 25. SQLAlchemy Guidelines

Prefer SQLAlchemy 2.x style APIs and modern typing patterns.

Recommended concepts:

- `Mapped[...]`
- `mapped_column(...)`
- explicit relationships
- reusable session configuration
- repository encapsulation
- explicit transaction handling

Keep common database concerns centralized.

```text
persistence/
├── models/
├── repositories/
├── queries/
└── unit_of_work.py
```

Avoid scattering database session creation throughout the codebase.

---

# 26. Async Architecture

If using asynchronous FastAPI endpoints and an async SQLAlchemy setup, keep the async boundary consistent.

Typical flow:

```text
Next.js
   ↓ HTTP
FastAPI async endpoint
   ↓ await
Async application service
   ↓ await
Async repository
   ↓ await
SQLAlchemy AsyncSession
   ↓
PostgreSQL
```

Do not blindly make every function `async`. Use asynchronous code where it provides value and ensure blocking operations do not accidentally run on the async request path.

---

# 27. Background Jobs and External Services

As the system grows, external integrations should not be injected directly into domain entities.

Use ports/interfaces:

```text
Service Layer
     ↓
EmailSender interface
     ↓
SMTP / Provider implementation
```

Similarly:

```text
Service
  ↓
FileStorage interface
  ↓
S3 / Object Storage implementation
```

For background jobs:

```text
API Request
    ↓
Application Service
    ↓
Queue / Job Dispatcher
    ↓
Worker
    ↓
Application Service / Use Case
```

Potential future infrastructure may include Redis, Celery/RQ/arq, object storage, or message brokers. The architecture should allow them to be added without contaminating domain logic.

---

# 28. External API / Integration Boundary

Treat third-party APIs as infrastructure.

Bad:

```text
Domain Entity → Stripe SDK
```

Better:

```text
Service
  ↓
PaymentGateway interface
  ↓
Stripe implementation
```

This makes testing easier and limits vendor-specific coupling.

---

# 29. Documentation Structure

Keep architectural information in `docs/`.

Recommended:

```text
docs/
├── architecture/
│   ├── overview.md
│   ├── layers.md
│   ├── dependency-rules.md
│   └── request-flow.md
│
├── api/
│   └── conventions.md
│
├── database/
│   ├── schema.md
│   └── migrations.md
│
└── decisions/
    ├── ADR-0001-layered-architecture.md
    ├── ADR-0002-postgresql.md
    └── ADR-0003-sqlalchemy.md
```

### ADRs — Architecture Decision Records

Use an ADR whenever an architectural decision has a meaningful long-term effect.

Template:

```text
# ADR-XXXX: Decision Title

## Status
Accepted

## Context
What problem are we solving?

## Decision
What are we choosing?

## Alternatives Considered
What else was evaluated?

## Consequences
What becomes easier/harder?
```

ADRs make the project **traceable over time**. Future developers can understand not only what the architecture is, but why it exists.

---

# 30. Request Traceability

Every important feature should be traceable through the architecture.

Use this chain as a standard mental model:

```text
Requirement
   ↓
API / UI Entry Point
   ↓
Use Case
   ↓
Domain Rule
   ↓
Repository Contract
   ↓
Persistence Implementation
   ↓
Database Structure
```

For example:

```text
"Create project"
      ↓
POST /api/v1/projects
      ↓
CreateProjectUseCase
      ↓
Project.create(...)
      ↓
ProjectRepository.add(...)
      ↓
SQLAlchemyProjectRepository.add(...)
      ↓
INSERT INTO projects ...
```

When debugging or modifying functionality, walk this chain rather than searching the entire repository randomly.

---

# 31. Recommended Development Workflow

Use an architecture-first implementation sequence.

## Step 1 — Define the boundary

Clarify:

- What enters the system?
- What leaves the system?
- What is the application operation?
- What business rule is involved?
- What data must be persisted?

## Step 2 — Define the Domain

Create or update:

```text
entities/
value_objects/
enums/
exceptions/
```

## Step 3 — Define application use cases

Example:

```text
services/use_cases/create_project.py
```

## Step 4 — Define repository contracts

Specify the persistence operations needed by the use case.

## Step 5 — Implement persistence

Create:

```text
SQLAlchemy model
repository implementation
migrations
queries/indexes where needed
```

## Step 6 — Expose the API

Add:

```text
Pydantic request schema
endpoint
response schema
error mapping
```

## Step 7 — Connect frontend

Add:

```text
API client
feature service/hook
UI
loading/error states
```

## Step 8 — Add tests

Test from the inside out:

```text
Domain → Service → Persistence/API → E2E
```

---

# 32. Git and Change Management

Keep commits focused on one architectural concern.

Prefer:

```text
feat: add project creation use case
feat: add project persistence repository
feat: expose project creation endpoint
feat: connect project creation form
```

Over:

```text
update everything
fix backend frontend database stuff
```

For larger teams, pull requests should make architectural boundaries visible.

A PR should answer:

- Which layer changed?
- Why did it change?
- Which dependency direction changed, if any?
- Which migrations were added?
- Which tests cover the change?

---

# 33. Code Review Checklist

Use this as a reusable review checklist.

### Architecture

- [ ] Is the code in the correct layer?
- [ ] Is dependency direction respected?
- [ ] Is business logic in the Domain/Service layer rather than the controller/UI?
- [ ] Are persistence details isolated?
- [ ] Are external services behind abstractions where appropriate?

### Backend

- [ ] Are endpoints thin?
- [ ] Are Pydantic schemas separate from ORM models?
- [ ] Are transactions explicit?
- [ ] Are database queries located in Persistence?
- [ ] Are errors mapped at the correct boundary?

### Frontend

- [ ] Is API communication centralized?
- [ ] Are feature-specific components kept inside their feature?
- [ ] Are UI concerns separate from backend infrastructure concerns?

### Database

- [ ] Is there a migration for the schema change?
- [ ] Are indexes/constraints appropriate?
- [ ] Is destructive behavior intentional?

### Testing

- [ ] Are domain rules unit tested?
- [ ] Are repository implementations integration tested?
- [ ] Are important end-to-end workflows covered?

---

# 34. Anti-Patterns to Avoid

## Fat Controllers

```text
Route
 ├── validate business rule
 ├── query database
 ├── send email
 ├── calculate values
 └── build response
```

Move those responsibilities into appropriate layers.

## Fat ORM Models

Avoid placing the entire business system inside SQLAlchemy models merely because they hold the data.

## God Services

Avoid one `ProjectService` becoming a 2,000-line class.

Split by use case or coherent responsibility.

## Generic `utils.py` Dumping Ground

Do not put unrelated business logic into:

```text
utils.py
helpers.py
common.py
```

Name the abstraction according to what it actually does.

## Circular Dependencies

Example of a bad dependency graph:

```text
Service → Persistence → Service
```

Refactor shared abstractions or interfaces so the dependency direction remains clear.

## Direct DB Calls Everywhere

Avoid:

```python
session.execute(...)
```

inside arbitrary endpoints, UI code, domain services, and helper files.

---

# 35. When the Project Gets Larger

Layered architecture should evolve rather than be abandoned.

A useful progression is:

```text
Stage 1
Simple Layered Monolith

Stage 2
Layered + Feature Modules

Stage 3
Modular Monolith

Stage 4
Selected components extracted into services only when justified
```

Do not split into microservices merely because the project has many folders.

A modular monolith can provide strong boundaries, independent testing, clear ownership, and simpler deployment while the product is still evolving.

---

# 36. Suggested Module Boundary Pattern

For a large project, think in terms of:

```text
Feature / Bounded Context
│
├── Presentation
├── Application / Services
├── Domain
└── Persistence
```

For example:

```text
modules/
├── identity/
│   ├── presentation/
│   ├── application/
│   ├── domain/
│   └── persistence/
│
├── projects/
│   ├── presentation/
│   ├── application/
│   ├── domain/
│   └── persistence/
│
└── notifications/
    ├── presentation/
    ├── application/
    ├── domain/
    └── persistence/
```

This is an optional evolution of the initial structure. Use it when the number of features/modules makes the central layer folders difficult to navigate.

---

# 37. Recommended Dependency Policy for a Generic Template

A project can encode these rules mechanically with linters, import rules, review checklists, or static analysis.

Conceptually:

```text
presentation  → application/services
application   → domain + abstractions
persistence   → domain + abstractions
infrastructure → interfaces/contracts

domain        → domain only
```

The domain should be the most portable part of the system.

If FastAPI is replaced, the domain should survive.

If PostgreSQL is replaced, the domain should survive.

If Next.js is replaced, the backend domain should survive.

If SQLAlchemy is replaced, the domain should survive.

That is one of the strongest indicators that the architecture is keeping the correct boundaries.

---

# 38. Tooling Baseline

## Frontend

Recommended baseline tools:

- Next.js
- TypeScript
- Tailwind CSS
- ESLint
- Prettier
- TypeScript strict mode
- A testing framework suitable for the application (for example, Vitest/Jest + React Testing Library)

## Backend

Recommended baseline tools:

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic
- pytest
- Ruff
- MyPy or another type-checking strategy if desired

## Database

- PostgreSQL
- Migration tooling
- Local database via Docker during development when appropriate

## Infrastructure

- Docker / Docker Compose for reproducible local environments
- CI pipeline for tests, linting, type checks, and build validation

Tool choices can change. The architecture should not become dependent on a specific editor, CI provider, or deployment platform.

---

# 39. Example Backend Package Layout

A concrete starter package can look like this:

```text
apps/api/app/
│
├── core/
│   ├── config.py
│   ├── logging.py
│   ├── security.py
│   └── errors.py
│
├── presentation/
│   ├── api/
│   │   ├── router.py
│   │   └── v1/
│   │       ├── router.py
│   │       └── endpoints/
│   ├── schemas/
│   └── exception_handlers.py
│
├── services/
│   ├── interfaces/
│   │   └── repositories/
│   ├── use_cases/
│   ├── application_services/
│   └── dto/
│
├── domain/
│   ├── entities/
│   ├── value_objects/
│   ├── services/
│   ├── events/
│   ├── enums.py
│   └── exceptions.py
│
├── persistence/
│   ├── models/
│   ├── repositories/
│   ├── mappers/
│   ├── queries/
│   └── unit_of_work.py
│
├── database/
│   ├── session.py
│   ├── base.py
│   ├── migrations/
│   └── seed/
│
└── main.py
```

This should be considered a **starting point**, not a requirement that every future project copy every folder.

Empty folders should not be created merely to satisfy the diagram. Introduce a directory when there is an actual reason to organize multiple related files there.

---

# 40. Recommended Frontend Package Layout

```text
apps/web/src/
│
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   ├── loading.tsx
│   ├── error.tsx
│   └── ...
│
├── components/
│   ├── ui/
│   └── shared/
│
├── features/
│   ├── auth/
│   ├── projects/
│   └── ...
│
├── services/
│   ├── api-client.ts
│   └── endpoints/
│
├── hooks/
├── lib/
├── types/
└── styles/
```

Next.js's App Router conventions remain in `app/`. Business/application logic should not be forced into `app/` simply because the framework owns that folder.

---

# 41. Operational Separation

Keep source code separate from operational artifacts.

```text
devtreck/
├── apps/
├── packages/
├── infra/
├── docs/
└── scripts/
```

This prevents Docker files, deployment manifests, maintenance scripts, documentation, and application logic from becoming mixed together.

---

# 42. CI/CD Quality Gate

A minimum CI pipeline should verify:

```text
Install dependencies
      ↓
Lint
      ↓
Type check
      ↓
Unit tests
      ↓
Integration tests
      ↓
Build frontend/backend artifacts
```

For migration changes, include a database test stage when practical.

The purpose is to make architecture and quality checks executable rather than purely documented.

---

# 43. Definition of Done for an Architectural Change

A change is not complete merely because the endpoint works.

Consider it complete when the appropriate pieces are addressed:

```text
[ ] Correct layer selected
[ ] Domain rules represented correctly
[ ] Application/use-case flow implemented
[ ] Repository contract updated if needed
[ ] Persistence implementation updated
[ ] Migration created if DB changes
[ ] API schemas updated
[ ] Frontend contract/client updated if needed
[ ] Tests added at the appropriate levels
[ ] Logging/observability considered
[ ] Documentation/ADR updated if architectural behavior changed
```

Not every change requires every box, but every box should be considered.

---

# 44. Architectural Principles to Keep Long-Term

These principles are more important than the exact folder names.

### Separation of Concerns

One component should have one primary reason to change.

### Explicit Dependencies

Dependencies should be visible and intentional.

### Stable Business Core

Business rules should not be tightly coupled to frameworks.

### Thin Boundaries

Controllers, routes, and UI components should remain lightweight.

### Testability

Core logic should be testable without PostgreSQL, HTTP, or a browser whenever possible.

### Traceability

A requirement should be traceable from entry point to domain rule to persistence.

### Replaceability

Frameworks and infrastructure should be replaceable without rewriting business logic.

### Incremental Complexity

Do not add abstractions, folders, services, or distributed components before they solve a real problem.

---

# 45. Generic Blueprint for Future Projects

This architecture is intended to be reused.

For a new project, start from:

```text
Project Root
│
├── apps/
│   ├── web/
│   └── api/
│
├── packages/
├── infra/
├── docs/
└── README.md
```

Then adapt the internals to the project's technologies.

For example:

```text
Presentation
  Next.js / React / REST / GraphQL / FastAPI / CLI

Service
  Use Cases / Application Services

Domain
  Entities / Value Objects / Domain Services / Events

Persistence
  Repositories / ORM / Query Layer

Database
  PostgreSQL / MySQL / SQLite / another storage system
```

The architectural contract stays conceptually the same even when technologies change.

---

# 46. Final Mental Model

When deciding where a new file belongs, ask these questions in order:

### Question 1 — Is this about communication?

HTTP, UI, request/response, serialization, routing?

→ **Presentation**

### Question 2 — Is this about executing an application operation?

Workflow, orchestration, transaction boundary, repository coordination?

→ **Service / Application**

### Question 3 — Is this a business rule or business concept?

Entity, value object, domain invariant, domain calculation?

→ **Domain**

### Question 4 — Is this about storing/retrieving data?

SQLAlchemy, repositories, database queries, mapping?

→ **Persistence**

### Question 5 — Is this about physical database structure?

Tables, indexes, constraints, migrations, PostgreSQL configuration?

→ **Database**

If the answer is unclear, the responsibility may be mixed and the design should be reconsidered before adding the file.

---

# 47. One-Page Architecture Summary

```text
                         DEVTRACK / FUTURE PROJECT

┌────────────────────────────────────────────────────────────┐
│ PRESENTATION                                               │
│ Next.js UI • FastAPI Routes • Pydantic Schemas • HTTP      │
└──────────────────────────────┬─────────────────────────────┘
                               │
                               ▼
┌────────────────────────────────────────────────────────────┐
│ SERVICE / APPLICATION                                      │
│ Use Cases • Orchestration • Transactions • DTOs            │
└──────────────────────────────┬─────────────────────────────┘
                               │
                               ▼
┌────────────────────────────────────────────────────────────┐
│ DOMAIN                                                     │
│ Entities • Value Objects • Business Rules • Domain Events   │
└──────────────────────────────▲─────────────────────────────┘
                               │
                               │ contracts / abstractions
                               │
┌──────────────────────────────┴─────────────────────────────┐
│ PERSISTENCE                                                 │
│ Repositories • SQLAlchemy • Mappers • Queries • UoW        │
└──────────────────────────────┬─────────────────────────────┘
                               │
                               ▼
┌────────────────────────────────────────────────────────────┐
│ DATABASE                                                    │
│ PostgreSQL • Tables • Constraints • Indexes • Migrations   │
└────────────────────────────────────────────────────────────┘

                         SUPPORTING CONCERNS

          Core Config • Security • Logging • Observability
          Testing • Documentation • ADRs • CI/CD • Infra
```

---

# 48. Recommended Starting Rule Set

For the initial development of Devtreck, keep these rules visible in the repository:

```text
1. Keep FastAPI endpoints thin.
2. Put workflows in application services/use cases.
3. Put business invariants in the domain.
4. Keep SQLAlchemy code inside persistence.
5. Keep PostgreSQL structure represented through migrations.
6. Do not expose ORM models as the API contract.
7. Keep frontend API access centralized.
8. Use repository interfaces where persistence should be replaceable/testable.
9. Establish explicit transaction boundaries.
10. Add architectural tests/checks as the project grows.
11. Document important architectural decisions with ADRs.
12. Organize by feature when the project becomes large enough to need it.
13. Prefer a modular monolith before introducing microservices without a concrete need.
14. Keep the domain as independent from frameworks and infrastructure as practical.
15. Treat this structure as a blueprint, not a rigid rulebook.
```

---

# Conclusion

The objective of this architecture is not to create the maximum number of folders or abstractions. The objective is to create a **predictable system of boundaries**.

A developer should be able to look at any file and quickly answer:

```text
What responsibility does this file own?
What layer does it belong to?
Who is allowed to depend on it?
What should never be imported here?
Where do I go next to trace this behavior?
```

For Devtreck, this structure gives the project a stable foundation while remaining generic enough to serve as a blueprint for future applications using different frameworks, databases, or infrastructure.

The architecture should evolve with the application, but the core principle should remain:

> **Keep communication, application orchestration, business rules, persistence, and physical storage as distinct concerns with explicit boundaries and traceable dependencies.**
