# NoteFlow Infrastructure - variantă finală

Această infrastructură acoperă cerințele finale ale proiectului:

- 3 microservicii proprii: `auth-service`, `notes-service`, `notes-data-service`
- PostgreSQL
- Adminer
- Kong API Gateway
- Prometheus + Grafana
- Portainer
- Docker Compose
- Docker Swarm cu `stack.yml` și secțiuni `deploy`
- rețele separate logic
- CI/CD prin GitHub Actions în fiecare repo de serviciu

---

## 1. Pornire locală cu Docker Compose

Copiază variabilele:

```bash
cp .env.example .env
```

Pornește tot stack-ul:

```bash
docker compose -f docker-compose.dev.yml up -d --build
```

Verifică:

```bash
docker ps
```

---

## 2. URL-uri locale

| Componentă | URL |
|---|---|
| Kong proxy | http://127.0.0.1:8000 |
| Kong admin API | http://127.0.0.1:8005 |
| Auth direct | http://127.0.0.1:8001/docs |
| Notes direct | http://127.0.0.1:8002/docs |
| Notes Data direct | http://127.0.0.1:8003/docs |
| Adminer | http://127.0.0.1:8080 |
| Prometheus | http://127.0.0.1:9090 |
| Grafana | http://127.0.0.1:3000 |
| Portainer | http://127.0.0.1:9000 sau https://127.0.0.1:9443 |

Grafana default:

```text
user: admin
password: admin
```

Adminer:

| Câmp | Valoare |
|---|---|
| System | PostgreSQL |
| Server | postgres |
| Username | noteflow_user |
| Password | noteflow_pass |
| Database | noteflow |

---

## 3. Test prin Kong

Kong este punctul unic de intrare.

Register:

```bash
curl -X POST http://127.0.0.1:8000/auth/register   -H "Content-Type: application/json"   -d '{"username":"demo_user","email":"demo@example.com","password":"parola123"}'
```

Login:

```bash
curl -X POST http://127.0.0.1:8000/auth/login   -H "Content-Type: application/json"   -d '{"username":"demo_user","password":"parola123"}'
```

Creează notă:

```bash
TOKEN="pune_tokenul_aici"

curl -X POST http://127.0.0.1:8000/notes   -H "Authorization: Bearer $TOKEN"   -H "Content-Type: application/json"   -d '{"title":"Nota prin Kong","content":"Merge prin gateway"}'
```

Listează note:

```bash
curl -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8000/notes
```

---

## 4. Monitorizare

Prometheus citește metrici de la:

- `auth-service:8001/metrics`
- `notes-service:8002/metrics`
- `notes-data-service:8003/metrics`

În Prometheus verifică:

```text
Status -> Targets
```

Toate target-urile trebuie să fie `UP`.

Query-uri utile:

```promql
up
http_requests_total
rate(http_requests_total[1m])
histogram_quantile(0.95, sum by (job, le) (rate(http_request_duration_seconds_bucket[5m])))
```

Grafana are datasource-ul Prometheus și dashboard-ul provisionate automat.

---

## 5. Rețele separate logic

Proiectul nu folosește o singură rețea. Rețelele sunt:

| Rețea | Rol |
|---|---|
| `gateway_net` | Kong și serviciile publice |
| `app_net` | comunicare între microservicii |
| `data_net` | PostgreSQL, notes-data, auth, Adminer |
| `monitoring_net` | Prometheus/Grafana și serviciile monitorizate |
| `admin_net` | Adminer, Grafana, Portainer |
| `agent_net` | Portainer Agent în Swarm |

---

## 6. Docker Swarm

Pe manager:

```bash
docker swarm init --advertise-addr IP_MANAGER
```

Pe fiecare worker rulezi comanda primită de la manager, de forma:

```bash
docker swarm join --token TOKEN IP_MANAGER:2377
```

Verificare pe manager:

```bash
docker node ls
```

Trebuie să vezi:

- 1 manager
- 2 workers

---

## 7. Deploy în Swarm

Înainte de Swarm, imaginile microserviciilor trebuie să existe în Docker Hub. Workflow-urile CI/CD le publică automat.

Setează namespace-ul:

```bash
export DOCKERHUB_NAMESPACE=utilizatorul_tau_dockerhub
export IMAGE_TAG=latest
```

Deploy:

```bash
docker stack deploy -c stack.yml noteflow
```

Verificare:

```bash
docker stack services noteflow
docker stack ps noteflow
```

Ștergere stack:

```bash
docker stack rm noteflow
```

---

## 8. Portainer

Compose local:

```text
http://127.0.0.1:9000
```

Swarm:

- `portainer-agent` rulează global pe toate nodurile
- `portainer` rulează pe manager
- se văd serviciile, stack-urile, volumele, rețelele și nodurile Swarm

---

## 9. CI/CD

Fiecare microserviciu are workflow în:

```text
.github/workflows/docker-ci.yml
```

Pipeline-ul face:

1. checkout
2. instalare dependințe
3. teste cu `pytest`
4. build Docker image
5. push în Docker Hub

Ai nevoie de secrets în GitHub:

```text
DOCKERHUB_USERNAME
DOCKERHUB_TOKEN
```

Repo-ul de infrastructură are:

```text
.github/workflows/validate-infrastructure.yml
```

care validează Compose și stack-ul Swarm.

---

## 10. Checklist final pentru demo

- `docker compose -f docker-compose.dev.yml up -d --build`
- arăți containerele în Portainer
- arăți Kong ca punct unic de intrare
- faci register/login prin Kong
- creezi/listezi/modifici/ștergi note prin Kong
- arăți datele în Adminer
- arăți target-urile `UP` în Prometheus
- arăți dashboard-ul în Grafana
- arăți `stack.yml` cu `deploy`, replici și rețele separate
- arăți workflow-urile GitHub Actions
# trigger
