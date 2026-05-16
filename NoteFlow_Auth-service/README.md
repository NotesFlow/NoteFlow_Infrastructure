# NoteFlow Auth Service

`NoteFlow Auth Service` is the authentication microservice for the `NoteFlow` project.

Its responsibility is to manage user registration, login, password hashing, JWT token generation, and authenticated user validation.

This service is part of a larger microservices architecture that includes:

- `auth-service`
- `notes-service`
- `notes-data-service`
- `postgres`
- infrastructure components managed in the dedicated infrastructure repository

## Responsibilities

This service is responsible for:

- registering users
- validating user credentials
- hashing passwords securely
- issuing JWT access tokens
- returning the currently authenticated user

This service is not responsible for:

- note management
- note persistence
- API gateway logic
- monitoring and infrastructure concerns

## Implemented Features

The current MVP includes:

- `POST /register`
- `POST /login`
- `GET /me`
- `GET /health`
- `GET /health/db`

## Tech Stack

- Python 3.10
- FastAPI
- SQLAlchemy
- PostgreSQL
- PyJWT
- pwdlib with Argon2
- Docker
- pytest

## Project Structure

```text
app/
├── core/
│   ├── config.py
│   └── security.py
├── db/
│   ├── base.py
│   └── session.py
├── dependencies/
│   ├── __init__.py
│   └── auth.py
├── models/
│   ├── __init__.py
│   └── user.py
├── routers/
│   ├── __init__.py
│   └── auth.py
├── schemas/
│   ├── __init__.py
│   └── auth.py
└── main.py

tests/
├── conftest.py
└── test_auth.py

Dockerfile
requirements.txt
requirements-dev.txt
.env.example
```

## Environment Variables

Create a local `.env` file based on `.env.example`.

Example:

```env
AUTH_SERVICE_PORT=8001
APP_NAME=NoteFlow Auth Service
APP_VERSION=0.1.0
DEBUG=false

DATABASE_HOST=127.0.0.1
DATABASE_PORT=5433
DATABASE_NAME=noteflow
DATABASE_USER=noteflow_user
DATABASE_PASSWORD=noteflow_pass

JWT_SECRET_KEY=change_this_to_a_long_random_secret_key_32_chars_min
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Configuration Notes

- For local development from Linux or WSL, use `DATABASE_HOST=127.0.0.1`.
- Do not use `host.docker.internal` as the default local host unless your runtime environment specifically requires it.
- The service loads variables from the local `.env` file automatically.
- The service creates the `users` table on startup if it does not already exist.

## User Model

The service currently manages the `users` table with the following fields:

- `id`
- `username`
- `email`
- `password_hash`
- `created_at`

## Local Development

### 1. Create and activate a virtual environment

Linux / WSL:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

For local test execution:

```bash
pip install -r requirements-dev.txt
```

### 3. Start PostgreSQL

If you use the infrastructure repository:

```bash
cd ../NoteFlow_Infrastructure
docker compose -f docker-compose.dev.yml up -d
```

Make sure the PostgreSQL values from the infrastructure repository match the values in this service's `.env`.

### 4. Run the service

```bash
cd ../NoteFlow_Auth-service
uvicorn app.main:app --reload --port 8001
```

The service will be available at:

```text
http://127.0.0.1:8001
```

Swagger UI:

```text
http://127.0.0.1:8001/docs
```

## Docker

Build the image:

```bash
docker build -t noteflow-auth-service .
```

Run the container:

```bash
docker run --rm -p 8001:8001 --env-file .env noteflow-auth-service
```

Note:

- if the service runs inside Docker and PostgreSQL runs outside Docker, then `DATABASE_HOST` may need to be adjusted for that setup
- if both services run in Docker Compose, use the PostgreSQL service name as host

## Automated Tests

Run the test suite with:

```bash
pip install -r requirements-dev.txt
pytest
```

The current tests focus on the main authentication flow:

- register
- login
- authenticated `/me`
- duplicate registration rejection
- invalid login rejection
- invalid token rejection

## Manual Testing

### Swagger

Open:

```text
http://127.0.0.1:8001/docs
```

Recommended order:

1. `GET /health`
2. `GET /health/db`
3. `POST /register`
4. `POST /login`
5. `Authorize` with the returned bearer token
6. `GET /me`

## API Endpoints

### `GET /health`

Checks whether the service is running.

Example response:

```json
{
  "status": "ok",
  "service": "NoteFlow Auth Service",
  "version": "0.1.0"
}
```

### `GET /health/db`

Checks whether the service can connect to PostgreSQL.

Example response:

```json
{
  "status": "ok",
  "database": "connected"
}
```

### `POST /register`

Creates a new user.

Request body:

```json
{
  "username": "albert",
  "email": "albert@example.com",
  "password": "parola123"
}
```

Successful response:

```json
{
  "id": 1,
  "username": "albert",
  "email": "albert@example.com"
}
```

Validation rules:

- `username` is required
- `username` length must be between 3 and 50 characters
- `email` must be valid
- `password` length must be between 6 and 100 characters
- username and email must be unique

### `POST /login`

Authenticates a user and returns a JWT access token.

Request body:

```json
{
  "username": "albert",
  "password": "parola123"
}
```

Successful response:

```json
{
  "access_token": "jwt_token_here",
  "token_type": "bearer"
}
```

### `GET /me`

Returns the current authenticated user.

Required header:

```text
Authorization: Bearer <access_token>
```

Successful response:

```json
{
  "id": 1,
  "username": "albert",
  "email": "albert@example.com",
  "created_at": "2026-04-24T06:30:45.502685Z"
}
```

## Error Cases

Typical error responses include:

- `400 Bad Request`
  - duplicate username or email during registration
- `401 Unauthorized`
  - invalid username or password
  - invalid token
  - missing authorization token
- `422 Unprocessable Entity`
  - invalid request body

## Security Notes

- Passwords are stored as hashes, never in plain text.
- JWT tokens are signed using the configured secret key.
- Use a strong `JWT_SECRET_KEY` outside development.
- Do not commit real secrets to the repository.

## Current Status

The service is currently suitable for the authentication part of the MVP and has been manually verified for:

- registration
- login
- bearer token authentication
- authenticated user retrieval
- database connectivity

## Next Integration Point

This service is expected to be consumed later by:

- `notes-service`, for authenticated access control
- `kong`, as the public gateway route for `/auth`
