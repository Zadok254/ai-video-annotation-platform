# AI Video Annotation Platform

An enterprise-grade, AI-assisted workspace for teams annotating video datasets they own or are authorized to process.

The platform is deliberately designed as a modular system: a Next.js client, a FastAPI domain API, asynchronous media and inference workers, PostgreSQL as the system of record, and object storage for immutable media artifacts. It supports human-in-the-loop review rather than autonomous decision making.

## First delivery slice

This repository begins with the **identity, tenancy, project, and dataset foundation**. It establishes secure token handling, role-based authorization, auditable ownership boundaries, and the project/dataset APIs that every media and annotation workflow depends on.

## Repository layout

```text
backend/       FastAPI application, domain services, database migrations, and tests
frontend/      Next.js annotation workspace (introduced after the API contract is stable)
ai/            Replaceable model adapters and inference orchestration
workers/       Celery workloads for media and inference processing
infra/         Container, deployment, and observability configuration
docs/          Product, architecture, security, and operating documentation
sdk/           Typed clients and integration helpers
tests/         End-to-end, performance, accessibility, and security suites
```

## Documentation

- [Product requirements](docs/PRD.md)
- [System architecture](docs/architecture/system-architecture.md)
- [Data model](docs/architecture/data-model.md)
- [Security baseline](docs/security.md)
- [Delivery roadmap](docs/roadmap.md)

## Local development

The API uses explicit environment configuration. Copy `.env.example` to an untracked `.env`, set strong development credentials, then start the dependency stack:

```bash
docker compose up --build
```

Run API checks from `backend/`:

```bash
python -m pip install -e '.[dev]'
pytest
ruff check .
ruff format --check .
```

The repository intentionally does not ship default secrets, permissive CORS, or automatic schema creation in production. Database changes are delivered through Alembic migrations.
