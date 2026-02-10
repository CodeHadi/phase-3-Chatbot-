# Todo Service - Technical Specification

Last updated: 2026-02-10

This document specifies the Todo service for Hackathon 3. It includes Machine-Callable-Procedure (MCP) tool definitions, the FastAPI stateless architecture, and SQLModel schemas for `Task`, `Conversation`, and `Message`. The design follows the Agentic Dev Stack workflow so agents can discover and call MCP tools safely.

**Goals**
- Provide a small, stateless REST API for todo management that can be called by agents and web UI.
- Expose machine-callable tools (MCP) for common operations: `add`, `list`, `complete`, `delete`, `update`.
- Use `FastAPI` + `SQLModel` for a typed, testable backend and provide JWT-based stateless auth.
- Record conversational context (optional) with `Conversation` and `Message` models to support agent interactions.

---

## 1. MCP Tool Definitions

All MCP tools are REST endpoints and also described as machine-callable tools (MCP). Each tool has a concise JSON input/output schema so agents can call them programmatically.

Tool naming conventions: `todo.add`, `todo.list`, `todo.complete`, `todo.delete`, `todo.update`.

1) todo.add
- Purpose: Create a new task for the authenticated user.
- HTTP: POST /api/tasks
- Input JSON:

```json
{
  "title": "string",
  "description": "string (optional)",
  "due_date": "ISO-8601 date-time (optional)",
  "metadata": {"object": "optional"}
}
```
- Output JSON (201):

```json
{
  "id": 123,
  "title": "...",
  "description": "...",
  "completed": false,
  "user_id": "user@example.com",
  "created_at": "2026-02-10T12:34:56Z"
}
```
- Errors: 400 (validation), 401 (unauthenticated)

2) todo.list
- Purpose: Return a page or list of tasks for the authenticated user.
- HTTP: GET /api/tasks
- Query params: `?completed=true|false` `?limit=50` `?offset=0`
- Output JSON (200): array of Task objects.

3) todo.complete
- Purpose: Mark a task completed or uncompleted.
- HTTP: PUT /api/tasks/{id}
- Input JSON:

```json
{ "completed": true }
```
- Output JSON: updated Task object (200).

4) todo.delete
- Purpose: Delete a task.
- HTTP: DELETE /api/tasks/{id}
- Output: 204 No Content on success; 404 if not found or not owned by the user.

5) todo.update
- Purpose: Update title, description, due_date, metadata.
- HTTP: PATCH /api/tasks/{id}
- Input JSON: any subset of Task writable fields.
- Output JSON: updated Task (200).

Note: All MCP tool definitions should be exported to the Agent Registry as part of Agentic Dev Stack boot sequence. Each tool should include an OpenAPI snippet and a concise natural-language description used by agents.

---

## 2. FastAPI Stateless Architecture

Overview:
- The API follows a stateless architecture: authentication is performed with bearer JWT tokens. No server-side session state is required to process requests.
- Each request must include `Authorization: Bearer <token>` except endpoints explicitly allowed for public access (e.g., `POST /api/auth/sign-in`, `POST /api/auth/sign-up` if enabled).

Key components:
- `main.py` — FastAPI app, startup/shutdown events, dependency wiring.
- `routes/` — route modules: `auth.py`, `tasks.py`, `conversations.py`.
- `dependencies.py` — `get_current_user()` dependency that validates the JWT and loads user identity; must raise `HTTPException(status_code=401)` if invalid.
- `database.py` — database URL configuration (support `DATABASE_URL` env var with `sqlite` fallback).

Security and tokens:
- Use HS256 or RS256 depending on key material. For Hackathon simplicity use HS256 with a strong secret stored in env var `BETTER_AUTH_SECRET`.
- Token payload minimal: `sub` (user id/email), `iat`, `exp`.
- Tokens expire (e.g., 1h) and can be renewed with refresh tokens optionally.

Scaling and statelessness:
- Because the server stores no session state, multiple FastAPI instances behind a load balancer can be used.
- Use a shared DB (Postgres/Neon) for persistent data; for local dev fallback to SQLite.

Performance and caching:
- Read-heavy endpoints (e.g., `todo.list`) may be cached via a distributed cache (Redis) if necessary. Cache keys must be user-scoped.

Observability:
- Add request logging middleware, structured logs, and metrics (Prometheus exporter) for latencies and error rates.

Rate limiting / abuse protection:
- Apply per-user and per-IP rate limits (e.g., 60/min) using an external rate limiter or middleware.

OpenAPI exposure:
- FastAPI automatically generates OpenAPI. MCP tool registry uses OpenAPI operation IDs and schemas.

---

## 3. SQLModel Schemas

These schemas are used with `SQLModel` (which extends Pydantic + SQLAlchemy). Keep models compact and indexed for user queries.

1) Task

```python
from typing import Optional, Dict
from sqlmodel import SQLModel, Field
from datetime import datetime

class TaskBase(SQLModel):
    title: str
    description: Optional[str] = None
    completed: bool = False
    due_date: Optional[datetime] = None
    metadata: Optional[Dict] = None

class Task(TaskBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    class Config:
        arbitrary_types_allowed = True
```

Indices and constraints:
- `user_id` indexed for fast per-user queries.
- Consider compound index `(user_id, completed)` if list queries commonly filter by completion.

2) Conversation

Purpose: store agent/user conversational context for longer-running tasks (optional feature).

```python
from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime

class Conversation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    title: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
```

3) Message

Purpose: represent a single message in a conversation (agent or user).

```python
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime

class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversation.id", index=True)
    role: str  # 'user' | 'agent' | 'system'
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Optionally store model metadata
    metadata: Optional[dict] = None
```

Relationships: use explicit queries (joins) to fetch conversation messages. Keep messages immutable; update only via append to preserve audit trails.

---

## 4. API Endpoint Mapping (summary)

- POST /api/auth/sign-up — create user (optional)
- POST /api/auth/sign-in — return JWT session
- POST /api/auth/sign-out — (stateless; can be a no-op or blacklist token server-side)
- GET /api/auth/session — optional, returns session data if token present

- GET /api/tasks — list tasks (MCP: `todo.list`)
- POST /api/tasks — create task (MCP: `todo.add`)
- GET /api/tasks/{id} — fetch task
- PUT /api/tasks/{id} — mark complete / replace (MCP: `todo.complete` can also be a PUT with only `completed`)
- PATCH /api/tasks/{id} — partial update (MCP: `todo.update`)
- DELETE /api/tasks/{id} — delete (MCP: `todo.delete`)

---

## 5. Agentic Dev Stack Workflow

This section describes how agents and automations interact with the service.

1) Discover
- Agents read the service manifest (OpenAPI + MCP registry) to discover `todo.*` tool definitions and usage examples.

2) Plan
- Agents create a short plan (list of MCP tool calls) to meet a high-level user goal (e.g., "Create 3 tasks and mark the first complete").

3) Act
- Agents invoke MCP endpoints over HTTP using service base URL and bearer token credentials.
- Calls must validate responses and back off on 5xx errors.

4) Observe
- Agents fetch task lists via `todo.list` to confirm changes. For critical flows, read-back is required.

5) Report
- Agents summarize actions to the user and optionally write a `Conversation` + `Message` entries to persist the dialog for later review.

Security and Safety within Agentic workflows:
- Agents must present a human-readable plan and obtain approval for destructive actions (deleting tasks).
- All agent calls must be authenticated and scoped to a user account; agent identity can be recorded in `Message.metadata`.

---

## 6. Implementation Notes

- Migrations: use `alembic` or `sqlmodel`-compatible migration tooling. Include a small migration to create `task`, `conversation`, `message` tables at startup for local dev.
- Tests: unit tests for each route, plus integration tests that run a test DB (sqlite in-memory) and exercise the MCP contract.
- Local dev: start FastAPI on `localhost:8000`, set `NEXT_PUBLIC_API_URL=http://localhost:8000` during frontend dev.
- Env vars: `DATABASE_URL`, `BETTER_AUTH_SECRET`, `JWT_ALGORITHM`.

Observability checklist:
- Structured logs (request-id), metrics for request durations, error counts.

---

## 7. Examples

Create a task (curl):

```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $JWT" \
  -H "Content-Type: application/json" \
  -d '{"title":"Buy milk","description":"2 liters"}'
```

Mark complete (MCP call):

```bash
curl -X PUT http://localhost:8000/api/tasks/123 \
  -H "Authorization: Bearer $JWT" \
  -H "Content-Type: application/json" \
  -d '{"completed":true}'
```

---

## 8. Security & Privacy Considerations

- Do not store plaintext passwords. Use `passlib[argon2]` to hash passwords (argon2id recommended).
- Protect JWT secret; prefer asymmetric signing (RS256) in production.
- Limit exposure of conversation data; provide opt-out for storing conversation logs.

---

## 9. Next Steps

- Add OpenAPI operationId and examples for all MCP tools so agents can parse and call them.
- Add example agent scripts that call the MCP tools following the Agentic Dev Stack plan→act→observe flow.

Additional notes:

- MCP endpoints include the `user_id` path parameter to preserve statelessness. Agents should call tools using the per-user path, for example:

  - `POST /api/mcp/{user_id}/todo.add`
  - `GET  /api/mcp/{user_id}/todo.list`

  The server will validate that the `user_id` path parameter equals the JWT `sub` claim and will return `403` on mismatch.

- Environment variables of interest:
  - `DATABASE_URL` (required in `.env` for Neon/Postgres production)
  - `BETTER_AUTH_SECRET` (JWT signing secret)
  - `JWT_ALGORITHM` (optional; default HS256)
  - `NEXT_PUBLIC_OPENAI_DOMAIN_KEY` (frontend ChatKit / domain-key integration)

File: [specs/todo-spec.md](specs/todo-spec.md)
