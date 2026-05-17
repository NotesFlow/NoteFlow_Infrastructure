# NoteFlow Infrastructure — Final Version

## Overview

NoteFlow Infrastructure reprezintă infrastructura completă pentru ecosistemul de microservicii NoteFlow.

Proiectul demonstrează:

- microservicii containerizate
- Docker Compose
- Docker Swarm
- Kubernetes
- Kong API Gateway
- PostgreSQL
- Adminer
- Prometheus + Grafana
- Portainer
- CI/CD cu GitHub Actions
- scaling și self-healing

---

# 1. Microservicii

| Serviciu | Rol |
|---|---|
| auth-service | autentificare și autorizare |
| notes-service | API principal pentru note |
| notes-data-service | persistență și management date |

---

# 2. Pornire locală cu Docker Compose

## Copiere variabile

```bash
cp .env.example .env
```

## Build și start stack

```bash
docker compose -f docker-compose.dev.yml up -d --build
```

## Verificare containere

```bash
docker ps
```

## Oprire stack

```bash
docker compose down
```

---

# 3. URL-uri locale

| Componentă | URL |
|---|---|
| Kong proxy | http://127.0.0.1:8000 |
| Kong admin API | http://127.0.0.1:8005 |
| Auth service | http://127.0.0.1:8001/docs |
| Notes service | http://127.0.0.1:8002/docs |
| Notes-data service | http://127.0.0.1:8003/docs |
| Adminer | http://127.0.0.1:8080 |
| Prometheus | http://127.0.0.1:9090 |
| Grafana | http://127.0.0.1:3000 |
| Portainer | http://127.0.0.1:9000 |

---

# 4. PostgreSQL + Adminer

## Login Adminer

| Câmp | Valoare |
|---|---|
| System | PostgreSQL |
| Server | postgres |
| Username | noteflow_user |
| Password | noteflow_pass |
| Database | noteflow |

---

# 5. Kong API Gateway

Kong este punctul unic de intrare în sistem.

## Verificare routes

```bash
curl http://127.0.0.1:8005/routes
```

## Verificare services

```bash
curl http://127.0.0.1:8005/services
```

## Register prin Kong

```bash
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"demo_user","email":"demo@example.com","password":"parola123"}'
```

## Login prin Kong

```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demo_user","password":"parola123"}'
```

## Creare notă prin Kong

```bash
TOKEN="pune_tokenul_aici"

curl -X POST http://127.0.0.1:8000/notes \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Nota prin Kong","content":"Merge prin gateway"}'
```

## Listare note prin Kong

```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:8000/notes
```

---

# 6. Monitorizare

## Prometheus

### Verificare targets

```text
Status -> Targets
```

Toate trebuie să fie `UP`.

## Query-uri Prometheus

```promql
up
```

```promql
http_requests_total
```

```promql
rate(http_requests_total[1m])
```

```promql
histogram_quantile(
  0.95,
  sum by (job, le) (
    rate(http_request_duration_seconds_bucket[5m])
  )
)
```

## Grafana

Login default:

```text
user: admin
password: admin
```

---

# 7. Docker Swarm

## Inițializare Swarm

```bash
docker swarm init --advertise-addr IP_MANAGER
```

## Join workers

```bash
docker swarm join --token TOKEN IP_MANAGER:2377
```

## Verificare noduri

```bash
docker node ls
```

## Deploy stack

```bash
export DOCKERHUB_NAMESPACE=utilizatorul_tau
export IMAGE_TAG=latest

docker stack deploy -c stack.yml noteflow
```

## Verificare servicii

```bash
docker stack services noteflow
```

## Verificare task-uri

```bash
docker stack ps noteflow
```

## Scaling

```bash
docker service scale noteflow_auth-service=4
```

## Restore

```bash
docker service scale noteflow_auth-service=2
```

## Ștergere stack

```bash
docker stack rm noteflow
```

---

# 8. Portainer

## Verificare servicii

```bash
docker service ls | grep portainer
```

## Access UI

```text
http://127.0.0.1:9000
```

## Funcționalități demonstrate

- containers
- services
- stacks
- scaling
- logs
- nodes
- volumes
- networks

---

# 9. Kubernetes

## Deploy namespace

```bash
kubectl apply -f k8s/namespace.yml
```

## Deploy infrastructură

```bash
kubectl apply -f k8s/
```

## Verificare pods

```bash
kubectl get pods -n noteflow
```

## Verificare servicii

```bash
kubectl get svc -n noteflow
```

## Logs

```bash
kubectl logs deployment/auth-service -n noteflow
```

## Scaling

```bash
kubectl scale deployment auth-service \
  --replicas=4 \
  -n noteflow
```

## Restore

```bash
kubectl scale deployment auth-service \
  --replicas=2 \
  -n noteflow
```

## Self-healing

```bash
kubectl delete pod -n noteflow -l app=auth-service
```

## Watch

```bash
kubectl get pods -n noteflow -w
```

---

# 10. CI/CD

## GitHub Actions

Workflow:

```text
.github/workflows/docker-ci.yml
```

## Pipeline

Pipeline-ul execută:

- checkout
- docker login
- build imagini
- push în Docker Hub

## GitHub Secrets

Necesare:

- DOCKERHUB_USERNAME
- DOCKERHUB_TOKEN

## Trigger pipeline

```bash
git add .
git commit -m "Trigger CI/CD"
git push origin andrei
```

---

# 11. Docker Images

Imagini publicate:

- noteflow-auth-service
- noteflow-notes-service
- noteflow-notes-data-service

---

# 12. Rețele separate logic

| Rețea | Rol |
|---|---|
| gateway_net | Kong și servicii publice |
| app_net | microservicii |
| data_net | PostgreSQL și servicii DB |
| monitoring_net | Prometheus și Grafana |
| admin_net | Adminer și Portainer |

---

# 13. Comenzi utile

## Docker

```bash
docker ps
docker images
docker service ls
docker stack services noteflow
docker stack ps noteflow
```

## Kubernetes

```bash
kubectl get pods -n noteflow
kubectl get svc -n noteflow
kubectl logs deployment/auth-service -n noteflow
```

## Kong

```bash
curl http://localhost:30081/routes
curl http://localhost:30081/services
```

## GitHub Actions

```bash
git push origin andrei
```

---

# 14. Concepte DevOps demonstrate

- microservices architecture
- API Gateway pattern
- container orchestration
- scaling
- self-healing
- observability
- monitoring
- CI/CD
- cloud-native deployment
- infrastructure automation
