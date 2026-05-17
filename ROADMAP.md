# NoteFlow Roadmap

Acest document urmărește pașii rămași pentru a duce NoteFlow de la MVP-ul actual la un proiect final, pregătit pentru demo.

Proiectul se dezvoltă incremental. Fiecare pas logic trebuie implementat, verificat, comis și împins pe remote înainte să trecem mai departe.

## Starea Curentă

MVP-ul aplicației este deja implementat și verificat local cu Docker Compose.

Componente finalizate:

- `auth-service`
- `notes-service`
- `notes-data-service`
- `postgres`
- `adminer`
- `docker-compose.dev.yml` local

Flux MVP verificat:

- register
- login
- creare notiță
- listare notițe
- editare notiță
- arhivare notiță
- pin notiță
- ștergere notiță
- verificarea datelor persistate în Adminer

## Decizie După Verificarea Branch-urilor

Andrei a lucrat pe branch-uri separate:

- `origin/Andrei` în `notes-service`
- `origin/Andrei` în `notes-data-service`
- `origin/andrei` în `infrastructure`

Decizie:

- Nu facem merge direct din aceste branch-uri în `main`.
- Continuăm lucrul pe `main`.
- Refolosim doar ideile utile din branch-ul de infrastructură.
- Reconstruim curat și incremental funcționalitățile rămase.

Motive:

- `notes-service` de pe `main` este deja mai avansat și mai curat.
- branch-ul de `notes-data-service` elimină sau slăbește funcționalități deja existente, cum ar fi archive, pin, Docker support și teste.
- branch-ul de `infrastructure` adaugă prea multe lucruri simultan și copiază codul microserviciilor în repo-ul de infrastructură.
- unele fișiere de monitorizare presupun existența endpoint-ului `/metrics`, dar serviciile actuale nu expun încă `/metrics`.
- fișiere precum `.DS_Store` nu trebuie integrate în repo.

Idei utile pe care le putem refolosi:

- rețele Docker explicite
- configurație declarativă pentru Kong
- structură pentru Prometheus și Grafana
- definiție pentru Portainer
- idee de `stack.yml` pentru Docker Swarm
- idee de GitHub Actions pentru build Docker

## Reguli Pentru Pașii Rămași

- Lucrăm pe `main`.
- Un pas logic înseamnă un commit.
- Testăm fiecare pas înainte de commit.
- Facem push după fiecare pas finalizat.
- Nu copiem codul microserviciilor în `NoteFlow_Infrastructure`.
- Păstrăm structura cu patru repo-uri:
  - `NoteFlow_Auth-service`
  - `NoteFlow_Notes-service`
  - `NoteFlow_Notes-Data-service`
  - `NoteFlow_Infrastructure`
- Fluxul MVP trebuie să rămână funcțional după fiecare schimbare de infrastructură.
- Nu adăugăm Kubernetes decât dacă devine explicit necesar mai târziu.

## Faza 1 - Rețele Docker Explicite

Obiectiv:

Separăm logic serviciile în `docker-compose.dev.yml`, fără să schimbăm comportamentul curent.

Fișiere:

- `NoteFlow_Infrastructure/docker-compose.dev.yml`
- `NoteFlow_Infrastructure/README.md`
- `NoteFlow_Infrastructure/.env.example`, doar dacă apar variabile sau porturi noi

Taskuri:

- [x] Adăugăm rețele Docker explicite:
  - `app_net`
  - `data_net`
  - `admin_net`
  - `gateway_net`
  - `monitoring_net`
- [x] Atașăm `postgres` doar la `data_net`.
- [x] Atașăm `auth-service` la `app_net` și `data_net`.
- [x] Atașăm `notes-data-service` la `app_net` și `data_net`.
- [x] Atașăm `notes-service` la `app_net`.
- [x] Atașăm `adminer` la `admin_net` și `data_net`.
- [x] Păstrăm porturile publice neschimbate:
  - `8001` pentru `auth-service`
  - `8002` pentru `notes-service`
  - `8003` pentru `notes-data-service`
  - `5433` pentru PostgreSQL
  - `8080` pentru Adminer
- [x] Rulăm `docker compose -f docker-compose.dev.yml config`.
- [x] Pornim stack-ul cu `docker compose -f docker-compose.dev.yml up -d --build`.
- [x] Verificăm toate endpoint-urile de health existente.
- [x] Retestăm fluxul MVP complet.
- [x] Actualizăm README-ul de infrastructură cu schema de rețele.

Notă de verificare:

- YAML-ul din `docker-compose.dev.yml` a fost validat local cu parser Python.
- `docker compose -f docker-compose.dev.yml config` a trecut.
- Stack-ul a pornit cu `docker compose -f docker-compose.dev.yml up -d --build`.
- Health check-urile pentru `auth-service`, `notes-service`, `notes-data-service`, `notes-data-service` DB și Adminer au trecut.
- Fluxul MVP complet a fost retestat cu succes după separarea rețelelor.

Gata când:

- toate serviciile existente încă funcționează
- Docker Compose creează rețelele explicite
- fluxul MVP complet trece
- Adminer încă se poate conecta la PostgreSQL

Commit propus:

```bash
git commit -m "Add explicit Docker networks for local stack"
```

## Faza 2 - Kong API Gateway

Obiectiv:

Introducem Kong ca punct unic de intrare pentru API-urile aplicației.

Fișiere:

- `NoteFlow_Infrastructure/docker-compose.dev.yml`
- `NoteFlow_Infrastructure/kong/kong.yml`
- `NoteFlow_Infrastructure/.env.example`
- `NoteFlow_Infrastructure/README.md`

Taskuri:

- [ ] Adăugăm serviciul `kong` în `docker-compose.dev.yml`.
- [ ] Configurăm Kong în mod DB-less.
- [ ] Adăugăm `kong/kong.yml`.
- [ ] Adăugăm ruta `/auth` către `auth-service`.
- [ ] Adăugăm ruta `/notes` către `notes-service`.
- [ ] Expunem portul proxy Kong, recomandat `8000`.
- [ ] Expunem portul admin Kong, recomandat `8005`.
- [ ] Atașăm Kong la `gateway_net` și `app_net`.
- [ ] Adăugăm variabilele de mediu:
  - `KONG_PROXY_PORT`
  - `KONG_ADMIN_PORT`
- [ ] Verificăm Kong Admin API.
- [ ] Testăm `POST /auth/register` prin Kong.
- [ ] Testăm `POST /auth/login` prin Kong.
- [ ] Testăm CRUD-ul de notițe prin Kong folosind tokenul primit la login.
- [ ] Actualizăm README-ul cu pașii de testare prin Kong.

Gata când:

- clientul poate folosi Kong pentru auth și operațiile pe notițe
- URL-urile directe ale serviciilor încă merg pentru debugging
- demo-ul poate arăta Kong ca API Gateway

Commit propus:

```bash
git commit -m "Add Kong gateway for auth and notes routes"
```

## Faza 3 - Metrici În Microservicii

Obiectiv:

Expunem metrici compatibile cu Prometheus din fiecare microserviciu FastAPI.

Implementare recomandată:

- folosim `prometheus-fastapi-instrumentator`
- expunem `/metrics`
- ascundem `/metrics` din Swagger dacă este practic

Repo-uri:

- `NoteFlow_Auth-service`
- `NoteFlow_Notes-service`
- `NoteFlow_Notes-Data-service`

Taskuri pentru fiecare serviciu:

- [ ] Adăugăm dependența de metrics în `requirements.txt`.
- [ ] Instrumentăm aplicația FastAPI.
- [ ] Expunem `/metrics`.
- [ ] Rulăm testele existente.
- [ ] Pornim serviciul și verificăm `/metrics`.
- [ ] Actualizăm README-ul serviciului.

Gata când:

- `http://127.0.0.1:8001/metrics` funcționează
- `http://127.0.0.1:8002/metrics` funcționează
- `http://127.0.0.1:8003/metrics` funcționează
- comportamentul API-urilor existente rămâne neschimbat

Commituri propuse:

```bash
git commit -m "Add Prometheus metrics to auth service"
git commit -m "Add Prometheus metrics to notes service"
git commit -m "Add Prometheus metrics to notes data service"
```

## Faza 4 - Prometheus Și Grafana

Obiectiv:

Adăugăm monitorizare pentru serviciile care rulează.

Fișiere:

- `NoteFlow_Infrastructure/docker-compose.dev.yml`
- `NoteFlow_Infrastructure/prometheus.yml`
- `NoteFlow_Infrastructure/grafana/provisioning/datasources/prometheus.yml`
- `NoteFlow_Infrastructure/grafana/provisioning/dashboards/noteflow.yml`
- `NoteFlow_Infrastructure/grafana/dashboards/noteflow-fastapi.json`
- `NoteFlow_Infrastructure/.env.example`
- `NoteFlow_Infrastructure/README.md`

Taskuri:

- [ ] Adăugăm serviciul `prometheus`.
- [ ] Adăugăm serviciul `grafana`.
- [ ] Adăugăm configurație Prometheus pentru:
  - `auth-service:8001/metrics`
  - `notes-service:8002/metrics`
  - `notes-data-service:8003/metrics`
- [ ] Adăugăm provisioning pentru datasource-ul Grafana.
- [ ] Adăugăm un dashboard Grafana simplu.
- [ ] Adăugăm variabilele de mediu:
  - `PROMETHEUS_PORT`
  - `GRAFANA_PORT`
  - `GRAFANA_ADMIN_USER`
  - `GRAFANA_ADMIN_PASSWORD`
- [ ] Atașăm Prometheus la `monitoring_net` și `app_net`.
- [ ] Atașăm Grafana la `monitoring_net` și `admin_net`.
- [ ] Pornim stack-ul.
- [ ] Deschidem Prometheus și verificăm că toate target-urile sunt `UP`.
- [ ] Deschidem Grafana și verificăm dashboard-ul.
- [ ] Generăm trafic prin Swagger sau Kong și verificăm că metricile se schimbă.
- [ ] Actualizăm README-ul cu pașii de monitorizare.

Gata când:

- Prometheus poate colecta date din toate cele trei servicii
- Grafana arată activitate live
- partea de monitorizare poate fi demonstrată

Commit propus:

```bash
git commit -m "Add Prometheus and Grafana monitoring stack"
```

## Faza 5 - Portainer

Obiectiv:

Adăugăm o interfață de administrare Docker pentru demo și inspecție.

Fișiere:

- `NoteFlow_Infrastructure/docker-compose.dev.yml`
- `NoteFlow_Infrastructure/.env.example`
- `NoteFlow_Infrastructure/README.md`

Taskuri:

- [ ] Adăugăm serviciul `portainer`.
- [ ] Montăm Docker socket.
- [ ] Adăugăm volum persistent `portainer_data`.
- [ ] Expunem Portainer pe portul `9000`.
- [ ] Adăugăm variabila de mediu:
  - `PORTAINER_PORT`
- [ ] Atașăm Portainer la `admin_net`.
- [ ] Pornim stack-ul.
- [ ] Deschidem UI-ul Portainer.
- [ ] Verificăm că se văd containerele, rețelele și volumele.
- [ ] Actualizăm README-ul cu pașii de setup inițial și notele de demo.

Gata când:

- Portainer rulează local
- stack-ul Docker Compose curent este vizibil în Portainer

Commit propus:

```bash
git commit -m "Add Portainer for Docker management"
```

## Faza 6 - Docker Swarm

Obiectiv:

Pregătim proiectul pentru deployment în Docker Swarm.

Fișiere:

- `NoteFlow_Infrastructure/stack.yml`
- `NoteFlow_Infrastructure/README.md`

Taskuri:

- [ ] Creăm `stack.yml`.
- [ ] Folosim imagini Docker în loc de build contexts locale.
- [ ] Definim rețele overlay:
  - `gateway_net`
  - `app_net`
  - `data_net`
  - `monitoring_net`
  - `admin_net`
- [ ] Adăugăm secțiuni `deploy` pentru servicii.
- [ ] Adăugăm politici de restart.
- [ ] Adăugăm replici unde are sens:
  - `auth-service`
  - `notes-service`
  - `notes-data-service`
  - `kong`
- [ ] Păstrăm PostgreSQL cu o singură replică.
- [ ] Adăugăm Portainer agent dacă este necesar pentru Swarm.
- [ ] Testăm `docker swarm init`.
- [ ] Testăm `docker stack deploy -c stack.yml noteflow`.
- [ ] Verificăm serviciile cu `docker stack services noteflow`.
- [ ] Verificăm fluxul aplicației prin Kong.
- [ ] Documentăm comenzile de pornire și curățare pentru Swarm.

Gata când:

- stack-ul se deployează în Swarm
- serviciile comunică prin rețele overlay
- demo-ul poate arăta servicii și replici în Swarm

Commit propus:

```bash
git commit -m "Add Docker Swarm stack configuration"
```

## Faza 7 - CI/CD

Obiectiv:

Automatizăm build-ul și publicarea imaginilor Docker.

Opțiune recomandată:

- GitHub Actions

Repo-uri:

- `NoteFlow_Auth-service`
- `NoteFlow_Notes-service`
- `NoteFlow_Notes-Data-service`
- opțional `NoteFlow_Infrastructure`

Taskuri:

- [ ] Adăugăm workflow GitHub Actions pentru `auth-service`.
- [ ] Adăugăm workflow GitHub Actions pentru `notes-service`.
- [ ] Adăugăm workflow GitHub Actions pentru `notes-data-service`.
- [ ] Rulăm testele în fiecare pipeline.
- [ ] Construim imaginea Docker în fiecare pipeline.
- [ ] Publicăm imaginea în Docker Hub.
- [ ] Folosim repository secrets:
  - `DOCKERHUB_USERNAME`
  - `DOCKERHUB_TOKEN`
- [ ] Folosim nume consistente pentru imagini.
- [ ] Actualizăm `stack.yml` ca să folosească imaginile publicate.
- [ ] Documentăm setup-ul CI/CD.

Gata când:

- un push pe `main` pornește pipeline-ul
- imaginile Docker sunt publicate cu succes
- Swarm poate face deploy folosind imaginile publicate

Commituri propuse:

```bash
git commit -m "Add Docker image CI pipeline"
git commit -m "Document CI/CD setup"
```

## Faza 8 - Documentație Finală Și Demo

Obiectiv:

Pregătim proiectul pentru prezentarea finală.

Fișiere:

- `CHANGELOG.md` din root
- `CHANGELOG-RO.md` din root
- `ROADMAP.md` din root
- README-urile serviciilor
- README-ul de infrastructură

Taskuri:

- [ ] Actualizăm fișierele de changelog cu fazele finalizate.
- [ ] Bifăm taskurile finalizate din roadmap.
- [ ] Actualizăm README-ul de infrastructură cu fluxul final de demo.
- [ ] Adăugăm URL-urile exacte pentru demo.
- [ ] Adăugăm credențiale exacte de demo unde este cazul.
- [ ] Adăugăm ordinea exactă pentru:
  - demo Docker Compose
  - demo Kong
  - demo Adminer
  - demo Grafana
  - demo Portainer
  - demo Swarm
  - demo CI/CD
- [ ] Verificăm toate comenzile înainte de prezentarea finală.
- [ ] Pregătim user și payload-uri de test.

Gata când:

- proiectul poate fi demonstrat de la zero
- echipa poate explica fiecare serviciu și fiecare componentă de infrastructură
- fluxul de demo este documentat și repetabil

Commit propus:

```bash
git commit -m "Document final demo workflow"
```

## Checklist Demo Final

- [ ] Arătăm repo-urile și structura proiectului.
- [ ] Pornim stack-ul Docker Compose.
- [ ] Arătăm containerele pornite.
- [ ] Arătăm endpoint-urile de health.
- [ ] Facem register.
- [ ] Facem login și obținem JWT.
- [ ] Creăm o notiță.
- [ ] Listăm notițele.
- [ ] Edităm o notiță.
- [ ] Arhivăm o notiță.
- [ ] Pin-uim o notiță.
- [ ] Ștergem o notiță.
- [ ] Verificăm datele în Adminer.
- [ ] Arătăm rutele Kong.
- [ ] Repetăm apelurile importante prin Kong.
- [ ] Arătăm target-urile Prometheus.
- [ ] Arătăm dashboard-ul Grafana.
- [ ] Arătăm UI-ul Portainer.
- [ ] Deployăm sau explicăm stack-ul Swarm.
- [ ] Arătăm workflow-ul CI/CD și imaginile Docker.
