# Project Overview

Todo Full-Stack App

- Frontend: Next.js (React) for UI and client-side routes.
- Backend: FastAPI serving JSON REST endpoints at `/api/*`.
- Database: Neon (Postgres) for persistence.
- Auth: JWT-based auth ("Better Auth JWT" approach) using `pyjwt` and refresh tokens.

Planned API endpoints (examples):

- `GET /api/tasks` — list tasks
- `POST /api/tasks` — create a task
- `GET /api/tasks/{id}` — fetch single task
- `PUT /api/tasks/{id}` — update task
- `DELETE /api/tasks/{id}` — delete task

Notes:
- Use `sqlmodel` for models + migrations against Neon.
- Use environment variables via `python-dotenv` for secrets and DB URL.
- Frontend will call backend API routes and handle auth via cookies or Authorization header.
