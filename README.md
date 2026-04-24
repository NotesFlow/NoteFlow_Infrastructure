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

Planned next additions, in order:

1. `adminer`
2. `auth-service`
3. `notes-data-service`
4. `notes-service`
5. full local verification of the core stack

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

At the moment it only provisions PostgreSQL. It will be extended step by step instead of adding the whole platform at once.

## Run Locally

Current command:

```bash
docker compose -f docker-compose.dev.yml up -d
```

Current useful command:

```bash
docker compose -f docker-compose.dev.yml down
```

## Working Rules

For this repository, the implementation order stays fixed:

1. core services first
2. local compose integration second
3. gateway after that
4. monitoring after that
5. swarm and ci/cd last

The infrastructure repo should never get ahead of the application itself.
