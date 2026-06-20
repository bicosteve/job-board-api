<div align="center">

# Job Board API

### A production-grade hiring platform — Flask · MySQL · Redis · React · TypeScript

**Full-stack. Fully tested. Fully documented. Ready to ship.**

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.3-000000?logo=flask&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?logo=mysql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7-DC382D?logo=redis&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white)
![Tests](https://img.shields.io/badge/Tests-unittest%20%2B%20coverage-success)
![License](https://img.shields.io/badge/license-MIT-blue)

[Live Demo](#) · [Swagger Docs](https://job-board-api-esrv.onrender.com/apidocs/) · [Frontend](https://bixx.co.ke/)

</div>

---

This project is a complete, deployed hiring marketplace. It covers the
full surface area of a real production service: secure auth, real-time data streams, a typed frontend, containerised infrastructure, and a comprehensive test suite.

---

## What it does

**Job Board API** is a two-sided hiring platform with distinct candidate and admin workflows:

- Candidates register, verify their email, build profiles, browse jobs, and apply — with a live application-status stream powered by Server-Sent Events.
- Admins post and manage jobs, review applications, and monitor a real-time firehose of all activity.
- Operators get a one-command Docker stack, a live Swagger UI at `/apidocs`, and a health endpoint for uptime monitoring.

---

## Architecture

Every request moves through three deliberate layers. No business logic leaks into controllers. No HTTP concerns reach the repositories.

```
┌──────────────────────────────────────────────────┐
│              React 18 + TypeScript (Vite)        │
│              typed api/client.ts                 │
└────────────────────┬─────────────────────────────┘
                     │  JSON / SSE over HTTP
                     ▼
┌──────────────────────────────────────────────────┐
│  controllers/     HTTP, auth, validation         │
└────────────────────┬─────────────────────────────┘
                     ▼
┌──────────────────────────────────────────────────┐
│  services/        Business rules, orchestration  │
└────────────────────┬─────────────────────────────┘
                     ▼
┌──────────────────────────────────────────────────┐
│  repositories/    SQL, connection pool, cache    │
└────────────────────┬─────────────────────────────┘
                     ▼
            ┌────────┴────────┐
            │   MySQL 8.0     │
            │   Redis 7       │
            └─────────────────┘
```

The same pattern — controllers, services, repositories — is mirrored across schemas (Marshmallow), docs (Swagger YAML per endpoint), and tests (unittest). The structure is consistent enough that a new engineer can orient in minutes.

---

## Engineering decisions worth noting

These are the choices that required trade-off thinking, not just implementation:

**Server-Sent Events for real-time streams** — chosen over WebSockets because application-status updates are server-initiated and unidirectional. SSE works over plain HTTP, requires no upgrade handshake, and survives most corporate proxies. The right tool for this load pattern.

**Redis-backed password reset tokens** — tokens are stored in Redis with a short TTL rather than a database column. This avoids schema migration overhead for ephemeral state, gives atomic expiry, and aligns with how session tokens are managed at scale.

**Versioned, ordered SQL schema files** — `tables/01.user.sql` through `tables/08.*.sql` are applied in sequence during bootstrap. No ORM migration framework dependency; the schema is readable SQL that any DBA can review and version-control clearly.

**Marshmallow for request/response validation** — every endpoint has an explicit schema. This means input is validated before it reaches the service layer, and response shapes are stable contracts rather than whatever the ORM happens to serialize.

**`docker-compose` with healthchecks on every service** — the backend container does not start until MySQL and Redis pass their health probes. This eliminates the entire class of "connection refused on startup" issues that plague naive Docker setups.

---

## Feature summary

### Candidate flows

- Registration with email verification (JWT-based)
- Profile and education history management
- Public job board: browse and view listings
- Job applications with optional resume upload
- Live application-status stream via SSE
- Self-service password reset (rate-limited: one request per 5 minutes)

### Admin flows

### Admin flows

- Separate registration and verification flow
- Job creation, editing, and listing
- Per-job application views
- Real-time application firehose (SSE)
- Application status updates

### Operational features

- Live Swagger UI: `GET /apidocs`
- Health probe: `GET /v0/api/health/check`
- Gunicorn WSGI for production
- Multi-stage production Docker image
- GitHub Actions pipeline for lint, test, image build, and Docker Hub push
- Redis-backed rate limiting for sensitive auth flows
- Environment-driven config: `dev` / `prod` / `docker`

---

## API reference

All endpoints are versioned under `/v0/api` and documented interactively at `/apidocs`.

| Method           | Endpoint                                             | Purpose                 |
| ---------------- | ---------------------------------------------------- | ----------------------- |
| `GET`            | `/health/check`                                      | Liveness probe          |
| `POST`           | `/user/register`                                     | Candidate signup        |
| `POST`           | `/user/verify`                                       | Email verification      |
| `POST`           | `/user/login`                                        | JWT issuance            |
| `GET`            | `/user/me`                                           | Authenticated profile   |
| `POST`           | `/user/request-reset`                                | Rate-limited reset code |
| `POST`           | `/user/reset-password`                               | Password reset          |
| `POST/GET`       | `/profile/create` · `/profile/get`                   | Profile CRUD            |
| `POST`           | `/education/create`                                  | Education record        |
| `POST/POST/POST` | `/admin/register` · `/admin/login` · `/admin/verify` | Admin auth              |
| `POST/GET/PUT`   | `/admin/jobs/create` · `/list` · `/<id>`             | Job management          |
| `GET/GET`        | `/public/jobs` · `/public/jobs/<id>`                 | Public listings         |
| `POST/GET`       | `/applications/job/create` · `/list`                 | Apply and list          |
| `GET/GET`        | `/applications/user/stream` · `/admin/stream`        | **SSE streams**         |
| `GET/GET`        | `/applications/user/list` · `/job/<id>`              | Filtered views          |
| `PUT`            | `/applications/job/update/<id>`                      | Status update           |
| `POST`           | `/files/upload`                                      | Resume upload           |

---

## Project structure

```
job-board-api/
├── app/
│   ├── __init__.py            # App factory, env-aware config wiring
│   ├── config.py              # BaseConfig / Dev / Prod / Docker
│   ├── routes.py              # Flask-RESTful resource registration
│   ├── controllers/           # HTTP layer — one module per domain
│   ├── services/              # Business logic — no HTTP, no SQL
│   ├── repositories/          # Data access — MySQL pool + Redis cache
│   ├── schemas/               # Marshmallow schemas (in + out)
│   ├── db/                    # Connection helpers
│   ├── docs/                  # Swagger YAML, one file per endpoint
│   └── utils/                 # Security, email, logger, helpers
├── frontend/                  # React 18 + TypeScript + Vite SPA
├── tables/                    # Ordered SQL schema files (01–08)
├── tests/                     # unittest: controllers, services, repos
├── docker-compose.yml
├── Dockerfile                 # production multi-stage image
├── .dockerignore              # excludes secrets, tests, frontend, dev artifacts
├── .github/workflows/ci.yml   # lint, tests, build_image, push_image
├── Pipfile / requirements.txt
├── Makefile                   # run / test / coverage / containers
└── .pre-commit-config.yml     # autopep8 + flake8
```

---

## Quick start

### Local

```bash
git clone https://github.com/bicosteve/job-board-api.git
cd job-board-api
pip install -r requirements.txt
# Run SQL files in order: tables/01.user.sql → tables/08.*.sql
python run.py
# Visit http://localhost:5005/apidocs
```

### Docker (recommended for local stack)

```bash
cp .env.docker.example .env.docker
make containers      # Builds and starts MySQL 8, Redis 7, Flask backend
make container_logs  # Tail logs
```

MySQL and Redis healthchecks run before the app starts. No manual sequencing needed.

### Production image

Build the production image locally:

```bash
docker build -f Dockerfile -t job-board-api:prod .
```

Run it with production-style settings:

```bash
docker run --rm -p 5005:5005 \
  -e ENV=prod \
  -e PORT=5005 \
  job-board-api:prod
```

The production image is a multi-stage build that:

- compiles dependency wheels in a builder stage
- installs only runtime dependencies in the final image
- runs as a non-root user
- serves the app with `gunicorn`
- exposes a healthcheck against `/v0/api/health/check`

### Frontend

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

---

## Testing and quality

```bash
make test       # python -m unittest discover -s tests
make coverage   # coverage run
make report     # coverage report -m
```

Tests cover controllers, services, repositories, helpers, and security utilities — the same surfaces that go to production.

Formatting and linting are configured so the tools agree with each other:

- `black` is pinned for consistent formatting
- `flake8` is aligned to an 88-character line length
- `autopep8` is configured to the same 88-character limit for CI consistency

This avoids formatter-vs-linter conflicts during local development and in GitHub Actions.

---

## Tech stack

**Backend** — Python 3.12 · Flask 2.3 · Flask-RESTful · Flask-CORS · Flask-Marshmallow · Flasgger · PyJWT · bcrypt · cryptography · PyMySQL · redis-py · Gunicorn

**Frontend** — React 18 · TypeScript 5 · Vite 5 · React Router 6

**Infrastructure** — Docker · Docker Compose · MySQL 8 · Redis 7 · pre-commit · Make

---

## Deployment notes

- `ProductionConfig` activates when `ENV=prod`; `DockerConfig` when `ENV=docker`
- `RENDER_EXTERNAL_HOSTNAME` and `FRONTEND_URL` are wired for Render, Railway, and Fly.io
- CORS origin, request size limit, and upload folder are all environment-driven
- Gunicorn is pinned in dependencies — no additional WSGI setup needed
- `Flask-Limiter` is enabled with Redis-backed storage for sensitive auth endpoints
- `packaging==24.2` is pinned to remain compatible with `limits==3.13.0`

### GitHub Actions container pipeline

The repository includes a CI workflow at `.github/workflows/ci.yml` with these stages:

1. **lint** — runs formatting and flake8 checks
2. **test** — runs the unittest suite and coverage gate
3. **build_image** — builds the production Docker image and stores it as a workflow artifact
4. **push_image** — pushes the built image to Docker Hub on pushes to `main`

Required Docker Hub secrets:

- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`

The published image name is derived from:

```yaml
IMAGE_NAME: ${{ secrets.DOCKERHUB_USERNAME }}/job-board-api
```

---

## Contact

**Steve Bico** · [github.com/bicosteve](https://github.com/bicosteve) ·
[LinkedIn](https://www.linkedin.com/in/bico-steve/) · [Email](bicosteve4@gmail.com)

---
