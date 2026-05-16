# NoteFlow Notes Service

Public notes microservice for the NoteFlow project.

This service sits between authenticated clients and `notes-data-service`. It accepts public note requests, resolves the authenticated user through `auth-service`, and forwards note operations to the internal data service.

## Responsibilities

This service is responsible for:

- exposing public note endpoints
- validating bearer tokens through `auth-service`
- extracting the authenticated `user_id`
- calling `notes-data-service` with validated payloads
- enforcing user-scoped access at the API layer

This service is not responsible for:

- user registration or login
- password hashing or JWT generation
- direct PostgreSQL access
- direct table creation or migrations

## Architecture Flow

```text
Client
  -> notes-service
      -> auth-service /me
      -> notes-data-service /internal/notes
          -> PostgreSQL
```

## Tech Stack

- Python 3.10
- FastAPI
- httpx
- Uvicorn
- pytest

## Project Structure

```text
app/
├── api/
│   └── routes/
│       ├── health.py
│       └── notes.py
├── core/
│   └── config.py
├── dependencies/
│   └── auth.py
├── schemas/
│   └── notes.py
├── services/
│   ├── auth_client.py
│   └── notes_data_client.py
└── main.py

tests/
└── test_health.py

Dockerfile
.dockerignore
requirements.txt
requirements-dev.txt
.env.example
```

## Environment Variables

Create `.env` from [.env.example](.env.example).

Local non-Docker example:

```env
NOTES_SERVICE_PORT=8002
AUTH_SERVICE_URL=http://127.0.0.1:8001
NOTES_DATA_SERVICE_URL=http://127.0.0.1:8003
REQUEST_TIMEOUT_SECONDS=5.0
```

Docker example when services are exposed on the host:

```env
AUTH_SERVICE_URL=http://host.docker.internal:8001
NOTES_DATA_SERVICE_URL=http://host.docker.internal:8003
```

## Run Locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8002
```

Swagger UI:

```text
http://127.0.0.1:8002/docs
```

## Run With Docker

```bash
docker build -t noteflow-notes-service .
docker run --rm -p 8002:8002 --env-file .env noteflow-notes-service
```

## Health Endpoint

### `GET /health`

Returns the service status:

```json
{
  "status": "ok",
  "service": "NoteFlow Notes Service",
  "version": "0.1.0"
}
```

## Public API Endpoints

All `/notes` endpoints require:

```http
Authorization: Bearer <access_token>
```

### `GET /notes`

Lists the authenticated user's notes.

### `POST /notes`

Creates a note for the authenticated user.

Request body:

```json
{
  "title": "My note",
  "content": "Example content"
}
```

### `PUT /notes/{note_id}`

Updates a note owned by the authenticated user.

Request body:

```json
{
  "title": "Updated title",
  "content": "Updated content"
}
```

### `DELETE /notes/{note_id}`

Deletes a note owned by the authenticated user.

### `PATCH /notes/{note_id}/archive`

Updates the archive state of a note.

Request body:

```json
{
  "is_archived": true
}
```

### `PATCH /notes/{note_id}/pin`

Updates the pin state of a note.

Request body:

```json
{
  "is_pinned": true
}
```

## Authentication Flow

1. The client logs in through `auth-service`.
2. The client receives a JWT access token.
3. The client sends requests to `notes-service` with `Authorization: Bearer <token>`.
4. `notes-service` calls `GET /me` on `auth-service`.
5. `notes-service` extracts the authenticated `user_id`.
6. `notes-service` calls `notes-data-service` with that `user_id`.

## Validation Rules

- the token must be valid
- the authenticated user must exist
- `user_id` is never accepted from the public request body
- all note operations are scoped to the authenticated user
- `title` is required and limited to 100 characters
- `content` may be empty

## Error Behavior

Expected responses:

- `401 Unauthorized` for missing or invalid authorization headers
- `401 Unauthorized` for invalid tokens
- `404 Not Found` when the note does not exist for the authenticated user
- `422 Unprocessable Entity` for invalid request payloads
- `503 Service Unavailable` when `auth-service` or `notes-data-service` cannot be reached

## Manual Testing

Use Swagger only:

```text
http://127.0.0.1:8002/docs
```

Recommended manual flow:

1. start `auth-service`
2. start `notes-data-service`
3. start `notes-service`
4. login through `auth-service`
5. copy the returned JWT
6. click `Authorize` in Swagger
7. test `GET /notes`
8. test `POST /notes`
9. test `PUT /notes/{note_id}`
10. test `PATCH /notes/{note_id}/archive`
11. test `PATCH /notes/{note_id}/pin`
12. test `DELETE /notes/{note_id}`

## Automated Tests

Current automated coverage includes:

- [tests/test_health.py](tests/test_health.py)
- [tests/test_notes.py](tests/test_notes.py)

The next useful step is adding tests for:

- full end-to-end integration with real `auth-service`
- full end-to-end integration with real `notes-data-service`
- additional edge cases around invalid payloads and upstream failures

## Current Status

Implemented:

- FastAPI bootstrap
- token validation through `auth-service`
- HTTP client for `notes-data-service`
- public note CRUD endpoints
- archive endpoint
- pin endpoint
- Docker support

## Next Step

The next implementation step is to harden this service before wider integration:

- remove remaining documentation drift
- add automated tests for `/notes`
- verify the full flow with `auth-service` and `notes-data-service`

* notes-service does not access PostgreSQL directly
* all persistence is delegated to notes-data-service
* architecture follows microservice separation of concerns

---
