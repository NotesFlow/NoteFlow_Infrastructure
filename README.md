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
- `kong`
- `prometheus`
- `grafana`
- `portainer`
- docker swarm

The base CI/CD setup is handled in the three microservice repositories through GitHub Actions.

## Current Status

Currently implemented in this repository:

- `postgres` in `docker-compose.dev.yml`
- `adminer` in `docker-compose.dev.yml`
- `auth-service` in `docker-compose.dev.yml`
- `notes-data-service` in `docker-compose.dev.yml`
- `notes-service` in `docker-compose.dev.yml`
- explicit Docker networks for local service separation
- `kong` in DB-less mode
- `prometheus` in `docker-compose.dev.yml`
- `grafana` in `docker-compose.dev.yml`
- `portainer` in `docker-compose.dev.yml`
- `stack.yml` for Docker Swarm deployment
- Docker Hub images referenced from `stack.yml`

## Local Stack Layout

The target local development stack is:

```text
Client
  -> kong
      -> auth-service
      -> notes-service
          -> auth-service /me
          -> notes-data-service
              -> postgres

Direct local debugging
  -> auth-service
  -> notes-service
      -> auth-service /me
      -> notes-data-service
          -> postgres

Adminer
  -> postgres

Prometheus
  -> auth-service /metrics
  -> notes-service /metrics
  -> notes-data-service /metrics

Grafana
  -> prometheus

Portainer
  -> Docker Engine through /var/run/docker.sock
```

For Docker-based local development, services should communicate through Docker DNS names, not through local WSL IP addresses.

Examples:

- `postgres`
- `auth-service`
- `notes-service`
- `notes-data-service`

## Local Docker Networks

The local Compose stack uses explicit bridge networks to keep service responsibilities clear:

```text
app_net
  kong
  auth-service
  notes-service
  notes-data-service

data_net
  postgres
  auth-service
  notes-data-service
  adminer

admin_net
  adminer
  grafana
  portainer

gateway_net
  kong

monitoring_net
  prometheus
  grafana
```

The current network rules are:

- `notes-service` can call `auth-service` and `notes-data-service` through `app_net`.
- `kong` can forward public traffic to `auth-service` and `notes-service` through `app_net`.
- `auth-service` can call `postgres` through `data_net`.
- `notes-data-service` can call `postgres` through `data_net`.
- `adminer` can inspect `postgres` through `data_net`.
- `gateway_net` is used by Kong as the public gateway layer.
- `prometheus` scrapes metrics from the FastAPI services through `app_net`.
- `grafana` reads metrics from Prometheus through `monitoring_net`.
- `portainer` is attached to `admin_net` and reads Docker state through the Docker socket mount.

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
KONG_PROXY_PORT=8000
KONG_ADMIN_PORT=8005
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=admin
PORTAINER_PORT=9000
```

These ports are the standard local ports we will keep across the project unless there is a concrete reason to change them.

## Current Compose File

- [docker-compose.dev.yml](docker-compose.dev.yml)

At the moment it provisions:

- `postgres`
- `adminer`
- `auth-service`
- `notes-data-service`
- `notes-service`
- `kong`
- `prometheus`
- `grafana`
- `portainer`

It will be extended step by step instead of adding the whole platform at once.

The core local stack is now functional and verified.

## Current Swarm Stack File

- [stack.yml](stack.yml)

The Swarm stack uses Docker Hub images for the three project microservices:

- `albertart10/noteflow-auth-service:latest`
- `albertart10/noteflow-notes-service:latest`
- `albertart10/noteflow-notes-data-service:latest`

These images are built and published by GitHub Actions from each service repository.

The Swarm stack provisions:

- `postgres`
- `auth-service`
- `notes-data-service`
- `notes-service`
- `kong`
- `adminer`
- `prometheus`
- `grafana`
- `portainer-agent`
- `portainer`

It uses overlay networks:

- `gateway_net`
- `app_net`
- `data_net`
- `monitoring_net`
- `admin_net`

## Run Locally

Current command:

```bash
docker compose -f docker-compose.dev.yml up -d
```

Current useful command:

```bash
docker compose -f docker-compose.dev.yml down
```

To rebuild services after code or configuration changes:

```bash
docker compose -f docker-compose.dev.yml up -d --build
```

## Run With Docker Swarm

The Swarm demo uses `stack.yml` and Docker Hub images.

Before deploying Swarm, make sure the GitHub Actions pipelines in the three service repositories have published the required images to Docker Hub.

If the Compose stack is already running, stop it before deploying the Swarm stack because both setups publish the same local ports:

```bash
docker compose -f docker-compose.dev.yml down
```

Initialize Swarm if it is not already active:

```bash
docker swarm init
```

Deploy the stack:

```bash
docker stack deploy -c stack.yml noteflow
```

Check services:

```bash
docker stack services noteflow
docker stack ps noteflow
```

Useful Swarm checks:

```bash
docker service ls
docker network ls
docker service logs noteflow_kong
```

Test the application through Kong:

```text
http://127.0.0.1:8000/auth/register
http://127.0.0.1:8000/auth/login
http://127.0.0.1:8000/notes
```

Remove the Swarm stack:

```bash
docker stack rm noteflow
```

Leave Swarm mode only if you no longer need it locally:

```bash
docker swarm leave --force
```

After removing the Swarm stack, the Compose stack can be started again with:

```bash
docker compose -f docker-compose.dev.yml up -d
```

## CI/CD Setup

Each microservice repository has a GitHub Actions workflow at:

- `.github/workflows/docker-image.yml`

The workflow runs on:

- push to `main`
- pull request to `main`
- manual `workflow_dispatch`

For each service, the workflow:

- installs Python dependencies
- runs `pytest`
- builds the Docker image
- publishes the image to Docker Hub on non-pull-request runs

Required GitHub Actions secrets in each microservice repository:

- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`

Docker Hub images:

- `albertart10/noteflow-auth-service`
- `albertart10/noteflow-notes-service`
- `albertart10/noteflow-notes-data-service`

Published tags:

- `latest`
- `sha-<commit-sha>`

## Verified Swarm Flow

The Swarm stack has been verified locally with:

```bash
docker stack deploy -c stack.yml noteflow
```

Verified Swarm services:

- `auth-service` with 2 replicas
- `notes-service` with 2 replicas
- `notes-data-service` with 2 replicas
- `kong` with 2 replicas
- `postgres` with 1 replica
- `adminer` with 1 replica
- `prometheus` with 1 replica
- `grafana` with 1 replica
- `portainer-agent` as a global service
- `portainer` with 1 replica

Verified through Kong:

- register -> `201`
- login -> `200`
- create note -> `201`
- list notes -> `200`
- update note -> `200`
- archive note -> `200`
- pin note -> `200`
- delete note -> `204`

Verified Swarm infrastructure:

- Prometheus targets are `UP`
- Grafana health returns `ok`
- Portainer runs with the Swarm agent and can inspect containers, networks, and volumes

## Currently Exposed Local Services

After starting the current stack, these services are available from the host:

- `postgres` on `127.0.0.1:5433`
- `adminer` on `127.0.0.1:8080`
- `auth-service` on `127.0.0.1:8001`
- `notes-data-service` on `127.0.0.1:8003`
- `notes-service` on `127.0.0.1:8002`
- `kong` proxy on `127.0.0.1:8000`
- `kong` admin API on `127.0.0.1:8005`
- `prometheus` on `127.0.0.1:9090`
- `grafana` on `127.0.0.1:3000`
- `portainer` on `127.0.0.1:9000`

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

## Notes Data Service In Compose

`notes-data-service` is also configured to connect to PostgreSQL through Docker DNS:

- `DATABASE_HOST=postgres`
- `DATABASE_PORT=5432`

The service is exposed locally on:

- `http://127.0.0.1:8003`

## Notes Service In Compose

`notes-service` is configured to call the other services through Docker DNS:

- `AUTH_SERVICE_URL=http://auth-service:8001`
- `NOTES_DATA_SERVICE_URL=http://notes-data-service:8003`

The service is exposed locally on:

- `http://127.0.0.1:8002`

## Kong Gateway In Compose

Kong runs in DB-less mode and reads its routes from:

- [kong/kong.yml](kong/kong.yml)

Current routes:

- `http://127.0.0.1:8000/auth` -> `auth-service`
- `http://127.0.0.1:8000/notes` -> `notes-service`

Kong Admin API is exposed locally on:

- `http://127.0.0.1:8005`

Useful checks:

```text
http://127.0.0.1:8005/services
http://127.0.0.1:8005/routes
```

## Monitoring In Compose

Prometheus reads its scrape configuration from:

- [prometheus.yml](prometheus.yml)

Current scrape targets:

- `auth-service:8001/metrics`
- `notes-service:8002/metrics`
- `notes-data-service:8003/metrics`

Prometheus is exposed locally on:

- `http://127.0.0.1:9090`

Useful Prometheus checks:

```text
http://127.0.0.1:9090/targets
```

Useful PromQL queries:

```promql
up
```

```promql
rate(http_requests_total[1m])
```

Grafana is exposed locally on:

- `http://127.0.0.1:3000`

Default local credentials:

- username: `admin`
- password: `admin`

Grafana provisioning files:

- [grafana/provisioning/datasources/prometheus.yml](grafana/provisioning/datasources/prometheus.yml)
- [grafana/provisioning/dashboards/noteflow.yml](grafana/provisioning/dashboards/noteflow.yml)
- [grafana/dashboards/noteflow-fastapi.json](grafana/dashboards/noteflow-fastapi.json)

Dashboard:

- `NoteFlow FastAPI Monitoring`

## Docker Management With Portainer

Portainer is exposed locally on:

- `http://127.0.0.1:9000`

The first time you open Portainer, create the local admin user from the setup screen.

After login, select or create the local Docker environment. If Portainer asks for the environment type, choose the local Docker standalone option that uses the Docker socket.

For demo purposes, use Portainer to show:

- running containers
- Docker networks
- Docker volumes
- container logs
- exposed ports
- container status

The Portainer container uses:

- `/var/run/docker.sock:/var/run/docker.sock` to read and manage the local Docker Engine
- `portainer_data:/data` to persist Portainer configuration

## Verified Local MVP Flow

The following flow has been verified successfully through the Docker Compose stack:

1. `POST /register`
2. `POST /login`
3. `POST /notes`
4. `GET /notes`
5. `PUT /notes/{id}`
6. `PATCH /notes/{id}/archive`
7. `PATCH /notes/{id}/pin`
8. `DELETE /notes/{id}`
9. update after delete returns `404`

Verified status codes:

- `register` -> `201`
- `login` -> `200`
- `create note` -> `201`
- `list notes` -> `200`
- `update note` -> `200`
- `archive note` -> `200`
- `pin note` -> `200`
- `delete note` -> `204`
- `update after delete` -> `404`

## Recommended Manual Workflow

1. Start the stack:

```bash
docker compose -f docker-compose.dev.yml up -d --build
```

2. Open Swagger for `auth-service`:

```text
http://127.0.0.1:8001/docs
```

3. Register and login a test user.

4. Copy the returned JWT access token.

5. Open Swagger for `notes-service`:

```text
http://127.0.0.1:8002/docs
```

6. Click `Authorize` and paste the Bearer token.

7. Test:

- `GET /notes`
- `POST /notes`
- `PUT /notes/{note_id}`
- `PATCH /notes/{note_id}/archive`
- `PATCH /notes/{note_id}/pin`
- `DELETE /notes/{note_id}`

8. Open Adminer:

```text
http://127.0.0.1:8080
```

9. Confirm that the `users` and `notes` tables contain the expected data.

## Recommended Kong Workflow

After the stack is running, Kong should be used as the public API entry point.

Use these URLs:

- `http://127.0.0.1:8000/auth/register`
- `http://127.0.0.1:8000/auth/login`
- `http://127.0.0.1:8000/notes`

The expected flow is:

1. Register through Kong:

```text
POST http://127.0.0.1:8000/auth/register
```

2. Login through Kong:

```text
POST http://127.0.0.1:8000/auth/login
```

3. Copy the JWT access token.

4. Use the token with the `notes` route through Kong:

```text
GET http://127.0.0.1:8000/notes
POST http://127.0.0.1:8000/notes
PUT http://127.0.0.1:8000/notes/{note_id}
PATCH http://127.0.0.1:8000/notes/{note_id}/archive
PATCH http://127.0.0.1:8000/notes/{note_id}/pin
DELETE http://127.0.0.1:8000/notes/{note_id}
```

The direct service URLs remain available for debugging:

- `http://127.0.0.1:8001/docs`
- `http://127.0.0.1:8002/docs`
- `http://127.0.0.1:8003/docs`

## Troubleshooting

### Port Variables In `.env`

The local `.env` file in this repository must contain all service ports:

- `POSTGRES_PORT`
- `ADMINER_PORT`
- `AUTH_SERVICE_PORT`
- `NOTES_DATA_SERVICE_PORT`
- `NOTES_SERVICE_PORT`
- `KONG_PROXY_PORT`
- `KONG_ADMIN_PORT`
- `PROMETHEUS_PORT`
- `GRAFANA_PORT`
- `PORTAINER_PORT`

If one of these variables is missing, Docker Compose may create the container with an empty port value or assign a random published port.

If that happens:

1. update `.env`
2. recreate the affected container

Example:

```bash
docker compose -f docker-compose.dev.yml up -d --force-recreate notes-service
```

### Recreating Services After Env Changes

If you change `.env` after a container was already created, the running container will not automatically pick up the new values.

Recreate the service explicitly:

```bash
docker compose -f docker-compose.dev.yml up -d --force-recreate auth-service
docker compose -f docker-compose.dev.yml up -d --force-recreate notes-data-service
docker compose -f docker-compose.dev.yml up -d --force-recreate notes-service
docker compose -f docker-compose.dev.yml up -d --force-recreate portainer
```

### Check Running Containers

Useful command:

```bash
docker ps
```

### Check Service Health Quickly

Useful endpoints:

- `http://127.0.0.1:8001/health`
- `http://127.0.0.1:8002/health`
- `http://127.0.0.1:8003/health`
- `http://127.0.0.1:8003/health/db`

## Working Rules

For this repository, the implementation order stays fixed:

1. core services first
2. local compose integration second
3. gateway after that
4. monitoring after that
5. docker management UI after monitoring
6. swarm and ci/cd last

The infrastructure repo should never get ahead of the application itself.
