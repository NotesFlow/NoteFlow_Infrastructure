# NoteFlow Notes Data Service

`notes-data-service` is the internal persistence microservice for the `NoteFlow` project.

It connects directly to PostgreSQL and manages the `notes` table. This service is intentionally simple: it does not authenticate users, does not validate JWT tokens, and is not meant to be called directly by an external client.

## Responsibilities

This service is responsible for:

- connecting to PostgreSQL
- creating and managing the `notes` table
- exposing internal CRUD endpoints for notes
- filtering all note operations by `user_id`

This service is not responsible for:

- registration or login
- JWT validation
- public API concerns
- higher-level note business rules that belong in `notes-service`

## Role In The Architecture

The expected application flow is:

1. the client calls `notes-service`
2. `notes-service` validates the authenticated user
3. `notes-service` calls `notes-data-service`
4. `notes-data-service` performs direct database operations

Within NoteFlow:

- `auth-service` handles identity and authentication
- `notes-service` handles public note endpoints and business logic
- `notes-data-service` handles direct note persistence

## Tech Stack

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Uvicorn

## Project Structure

```text
app/
  api/
    routes/
  core/
  db/
  dependencies/
  models/
  schemas/
  services/
  main.py
requirements.txt
requirements-dev.txt
.env.example
README.md
```

Directory purpose:

- `api/routes` contains the FastAPI routes
- `core` contains runtime configuration
- `db` contains the SQLAlchemy base, engine, and session setup
- `dependencies` contains reusable FastAPI dependencies
- `models` contains SQLAlchemy models
- `schemas` contains request and response models
- `services` contains note data operations

## Data Model

The service manages the `notes` table with this minimum structure:

- `id`: integer primary key
- `user_id`: integer not null
- `title`: string(100) not null
- `content`: text not null
- `is_archived`: boolean default false
- `is_pinned`: boolean default false
- `created_at`: datetime
- `updated_at`: datetime

Current SQLAlchemy model:

- [app/models/note.py](app/models/note.py)

## Business Rules At This Layer

The rules enforced here are intentionally minimal:

- a note is always associated with a `user_id`
- list operations are filtered by `user_id`
- update, delete, archive, and pin only affect notes owned by the provided `user_id`
- `title` is required
- `content` may be empty
- if a note does not exist for the given `user_id`, the service returns `404`

Authentication remains out of scope for this service.

## Environment Variables

The service uses environment-based configuration.

Defined in [.env.example](.env.example):

```env
NOTES_DATA_SERVICE_HOST=0.0.0.0
NOTES_DATA_SERVICE_PORT=8003

DATABASE_HOST=127.0.0.1
DATABASE_PORT=5433
DATABASE_NAME=noteflow
DATABASE_USER=noteflow_user
DATABASE_PASSWORD=noteflow_pass
```

Important local note:

- `DATABASE_HOST=127.0.0.1` is correct for the current local setup
- PostgreSQL is expected to be exposed on port `5433`

## Installation

Create and activate a virtual environment, then install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

For local test execution:

```bash
pip install -r requirements-dev.txt
```

Create a local `.env` file based on `.env.example`.

## Running PostgreSQL

The project currently uses PostgreSQL from the infrastructure repository.

Start it from:

```bash
cd /mnt/c/Users/Albert/Desktop/NoteFlow/NoteFlow_Infrastructure
docker compose -f docker-compose.dev.yml up -d
```

## Running The Service Locally

From the service repository:

```bash
cd /mnt/c/Users/Albert/Desktop/NoteFlow/NoteFlow_Notes-Data-service
source .venv/bin/activate
uvicorn app.main:app --reload --port 8003
```

Swagger UI:

```text
http://127.0.0.1:8003/docs
```

## Running With Docker

Build the image:

```bash
docker build -t noteflow-notes-data-service .
```

Run the container:

```bash
docker run --rm -p 8003:8003 --env-file .env noteflow-notes-data-service
```

Important Docker note:

- for local standalone Docker usage, `DATABASE_HOST` should point to the PostgreSQL host visible from the container runtime
- for Docker Compose usage inside the NoteFlow infrastructure stack, `DATABASE_HOST` should be `postgres`

## Automated Tests

Run the automated tests with:

```bash
pip install -r requirements-dev.txt
pytest
```

The current test suite covers:

- create note
- list notes
- update note
- archive note
- pin note
- delete note
- filtering by `user_id`
- `404` on note access after deletion

## Health Endpoints

### `GET /health`

Checks whether the service is running.

Example response:

```json
{
  "status": "ok",
  "service": "NoteFlow Notes Data Service",
  "version": "0.1.0"
}
```

### `GET /health/db`

Checks whether the service can reach PostgreSQL.

Example response:

```json
{
  "status": "ok",
  "database": "connected"
}
```

## Internal API Endpoints

These endpoints are internal and are meant to be called later by `notes-service`.

### `GET /internal/notes`

Returns notes for a given user.

Query parameters:

- `user_id`

Response:

- `200 OK`
- list of note objects

### `POST /internal/notes`

Creates a new note.

Request body:

```json
{
  "user_id": 1,
  "title": "My note",
  "content": "Example content"
}
```

Response:

- `201 Created`
- created note object

### `PUT /internal/notes/{note_id}`

Updates an existing note for the provided `user_id`.

Request body:

```json
{
  "user_id": 1,
  "title": "Updated title",
  "content": "Updated content"
}
```

Response:

- `200 OK`
- updated note object
- `404 Not Found` if the note does not belong to that `user_id`

### `DELETE /internal/notes/{note_id}`

Deletes a note for the provided `user_id`.

Query parameters:

- `user_id`

Response:

- `204 No Content`
- `404 Not Found` if the note does not belong to that `user_id`

### `PATCH /internal/notes/{note_id}/archive`

Changes the archive flag for a note.

Request body:

```json
{
  "user_id": 1,
  "is_archived": true
}
```

Response:

- `200 OK`
- updated note object

### `PATCH /internal/notes/{note_id}/pin`

Changes the pin flag for a note.

Request body:

```json
{
  "user_id": 1,
  "is_pinned": true
}
```

Response:

- `200 OK`
- updated note object

## Manual Testing

Use Swagger only.

Open:

```text
http://127.0.0.1:8003/docs
```

Recommended order:

1. `GET /health`
2. `GET /health/db`
3. `POST /internal/notes`
4. `GET /internal/notes`
5. `PUT /internal/notes/{note_id}`
6. `PATCH /internal/notes/{note_id}/archive`
7. `PATCH /internal/notes/{note_id}/pin`
8. `DELETE /internal/notes/{note_id}`

Suggested payloads:

Create note:

```json
{
  "user_id": 1,
  "title": "First internal note",
  "content": "Created from Swagger"
}
```

Update note:

```json
{
  "user_id": 1,
  "title": "Updated internal note",
  "content": "Updated from Swagger"
}
```

Archive note:

```json
{
  "user_id": 1,
  "is_archived": true
}
```

Pin note:

```json
{
  "user_id": 1,
  "is_pinned": true
}
```

For:

- `GET /internal/notes`
- `DELETE /internal/notes/{note_id}`

set `user_id` as a query parameter in Swagger.

## Validation And Error Behavior

Expected behavior:

- missing or invalid `user_id` -> validation error
- empty `title` -> validation error
- note not found for the given `user_id` -> `404`
- successful delete -> `204`

## Current Status

Current implementation status:

- FastAPI app bootstrap completed
- PostgreSQL wiring completed
- `notes` table setup completed
- internal CRUD endpoints completed
- verified against the local PostgreSQL container

Verified flow:

- create note
- list notes
- update note
- archive note
- pin note
- delete note
- `404` after attempting to modify a deleted note

## Next Integration Step

The next service to implement is `notes-service`.

That service will:

- validate the authenticated user
- expose public note endpoints
- call `notes-data-service`
- keep public business logic outside the persistence layer
