# NoteFlow — GitLab CI/CD

Acest proiect include pipeline GitLab CI/CD în fișierul:

```text
.gitlab-ci.yml
```

Pipeline-ul are 4 etape:

1. `validate` — validează `docker-compose.dev.yml` și `stack.yml`.
2. `test` — rulează testele Python pentru cele 3 microservicii.
3. `build` — construiește imaginile Docker și le publică în GitLab Container Registry.
4. `deploy` — deploy manual pe Docker Swarm prin SSH.

## Cum verifici CI/CD

1. Urcă proiectul într-un repo GitLab.
2. Fă push pe branch-ul `main`.
3. Intră în GitLab:

```text
CI/CD → Pipelines
```

Trebuie să vezi joburile:

```text
validate:compose-and-stack
 test:auth-service
 test:notes-service
 test:notes-data-service
 build:auth-service
 build:notes-service
 build:notes-data-service
 deploy:swarm
```

Dacă build-urile sunt verzi, partea CI este funcțională.

## Variabile necesare pentru deploy

În GitLab mergi la:

```text
Settings → CI/CD → Variables
```

Adaugă:

```text
SSH_PRIVATE_KEY       cheia privată SSH pentru serverul/managerul Swarm
DEPLOY_HOST           IP-ul sau domeniul managerului Docker Swarm
DEPLOY_USER           userul SSH, ex: ubuntu
JWT_SECRET_KEY        cheia JWT a aplicației
POSTGRES_PASSWORD     parola PostgreSQL
GRAFANA_ADMIN_PASSWORD parola admin Grafana
```

## Ce face deploy-ul

Jobul `deploy:swarm` copiază folderul `NoteFlow_Infrastructure` pe server și rulează:

```bash
docker stack deploy -c stack.yml noteflow --with-registry-auth
```

Asta reprezintă CD: deployment automatizat către Docker Swarm.

## Pentru demo

Arată în GitLab:

```text
CI/CD → Pipelines → ultimul pipeline → joburi verzi
```

Apoi arată în server:

```bash
docker service ls
```

și în browser:

```text
Kong:       http://SERVER:8000
Prometheus: http://SERVER:9090
Grafana:    http://SERVER:3000
Portainer:  https://SERVER:9443
```
