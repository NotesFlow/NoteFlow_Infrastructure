# NoteFlow Infrastructure

Infrastructure repository for the NoteFlow microservices project.

This repository contains the local Docker setup used to run the core application stack during development.

## Purpose

The infrastructure layer is introduced only after the core microservices are functional on their own.

At this stage, the goal is to support the local MVP flow:

- `auth-service`
- `notes-service`
- `notes-data-service`
- `postgres`
- `adminer`

The following components are intentionally postponed:

- `kong`
- `prometheus`
- `grafana`
- `portainer`
- `docker swarm`
- `ci/cd`

## Current Status

Currently implemented in this repository:

- `postgres` in `docker-compose.dev.yml`
- `adminer` in `docker-compose.dev.yml`
- `auth-service` in `docker-compose.dev.yml`

Planned next additions, in order:

1. `notes-data-service`
2. `notes-service`
3. full local verification of the core stack

## Local Stack Layout

The target local development stack is:

```text
Client
  -> auth-service
  -> notes-service
      -> auth-service /me
      -> notes-data-service
          -> postgres

Adminer
  -> postgres
```

For Docker-based local development, services should communicate through Docker DNS names, not through local WSL IP addresses.

Examples:

- `postgres`
- `auth-service`
- `notes-service`
- `notes-data-service`

## Environment Variables

Create `.env` from `.env.example`.

Current variables:

```env
POSTGRES_DB=noteflow
POSTGRES_USER=noteflow_user
POSTGRES_PASSWORD=noteflow_pass
POSTGRES_PORT=5433
ADMINER_PORT=8080
AUTH_SERVICE_PORT=8001
NOTES_SERVICE_PORT=8002
NOTES_DATA_SERVICE_PORT=8003
```

These ports are the standard local ports we will keep across the project unless there is a concrete reason to change them.

## Current Compose File

- [docker-compose.dev.yml](docker-compose.dev.yml)

At the moment it provisions:

- `postgres`
- `adminer`
- `auth-service`

It will be extended step by step instead of adding the whole platform at once.

## Run Locally

Current command:

```bash
docker compose -f docker-compose.dev.yml up -d
```

Current useful command:

```bash
docker compose -f docker-compose.dev.yml down
```

## Currently Exposed Local Services

After starting the current stack, these services are available from the host:

- `postgres` on `127.0.0.1:5433`
- `adminer` on `127.0.0.1:8080`
- `auth-service` on `127.0.0.1:8001`

## Database Access In Browser

After starting the local stack, Adminer is available at:

```text
http://127.0.0.1:8080
```

Use the following connection values:

- System: `PostgreSQL`
- Server: `postgres`
- Username: `noteflow_user`
- Password: `noteflow_pass`
- Database: `noteflow`

If you connect through Docker Compose networking, `postgres` is the correct server name because it is the Docker service name.

## Auth Service In Compose

`auth-service` is now configured to connect to PostgreSQL through the Docker service name:

- `DATABASE_HOST=postgres`
- `DATABASE_PORT=5432`

This is the correct local container-to-container setup and avoids WSL-specific IP workarounds.

## Working Rules

For this repository, the implementation order stays fixed:

1. core services first
2. local compose integration second
3. gateway after that
4. monitoring after that
5. swarm and ci/cd last

The infrastructure repo should never get ahead of the application itself.
