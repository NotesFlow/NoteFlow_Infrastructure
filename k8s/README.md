# NoteFlow Kubernetes Deployment

Acest folder contine manifestele Kubernetes pentru rularea proiectului NoteFlow pe clusterul local din Docker Desktop Kubernetes.

## Ce contine

- `Namespace` dedicat: `noteflow`
- `ConfigMap` pentru configuratie non-secreta
- `Secret` pentru parola PostgreSQL, cheia JWT si parola Grafana
- `PostgreSQL` cu `PersistentVolumeClaim`
- `auth-service`
- `notes-data-service`
- `notes-service`
- `Kong` ca API Gateway
- `Adminer` pentru inspectarea bazei de date
- `Prometheus` pentru colectarea metricilor
- `Grafana` cu datasource si dashboard provisionate automat

## Pornire

Din folderul `NoteFlow_Infrastructure`:

```bash
kubectl apply -f k8s/
```

Verificare:

```bash
kubectl get pods -n noteflow
kubectl get svc -n noteflow
kubectl get pvc -n noteflow
```

Toate podurile trebuie sa ajunga in starea `Running`, iar containerele trebuie sa fie `READY`.

## Expunere locala

Manifestele definesc servicii `NodePort`, dar pe unele instalari Docker Desktop Kubernetes accesul direct la `NodePort` din WSL poate sa nu fie publicat pe `127.0.0.1`. Varianta stabila pentru demo local este `kubectl port-forward`.

Porneste aceste comenzi in terminale separate:

```bash
kubectl port-forward -n noteflow svc/kong 30080:8000 30081:8001
kubectl port-forward -n noteflow svc/adminer 30088:8080
kubectl port-forward -n noteflow svc/prometheus 30090:9090
kubectl port-forward -n noteflow svc/grafana 30300:3000
```

Linkuri locale dupa port-forward:

- Kong proxy: `http://127.0.0.1:30080`
- Kong admin API: `http://127.0.0.1:30081`
- Adminer: `http://127.0.0.1:30088`
- Prometheus: `http://127.0.0.1:30090`
- Grafana: `http://127.0.0.1:30300`

## Date utile pentru demo

Adminer:

```text
System: PostgreSQL
Server: postgres
Username: noteflow_user
Password: noteflow_pass
Database: noteflow
```

Grafana:

```text
Username: admin
Password: admin
```

## Testare prin Kong

Register:

```http
POST http://127.0.0.1:30080/auth/register
Content-Type: application/json

{
  "username": "k8s_demo_user",
  "email": "k8s_demo_user@example.com",
  "password": "noteflow123"
}
```

Login:

```http
POST http://127.0.0.1:30080/auth/login
Content-Type: application/json

{
  "username": "k8s_demo_user",
  "password": "noteflow123"
}
```

Creare nota:

```http
POST http://127.0.0.1:30080/notes
Authorization: Bearer TOKEN
Content-Type: application/json

{
  "title": "Nota demo Kubernetes",
  "content": "Aceasta nota a fost creata prin Kong, pe Kubernetes."
}
```

Listare note:

```http
GET http://127.0.0.1:30080/notes
Authorization: Bearer TOKEN
```

## Swagger pentru verificari directe

Kong este gateway si nu genereaza Swagger propriu. Pentru Swagger direct pe servicii, foloseste port-forward doar in timpul testarii:

```bash
kubectl port-forward -n noteflow svc/auth-service 8001:8001
kubectl port-forward -n noteflow svc/notes-service 8002:8002
kubectl port-forward -n noteflow svc/notes-data-service 8003:8003
```

Apoi:

- `http://127.0.0.1:8001/docs`
- `http://127.0.0.1:8002/docs`
- `http://127.0.0.1:8003/docs`

## Monitorizare

Prometheus:

- deschide `http://127.0.0.1:30090`
- verifica `Status -> Targets`
- ruleaza query-uri precum `up`, `http_requests_total`, `http_request_duration_seconds_count`

Grafana:

- deschide `http://127.0.0.1:30300`
- login cu `admin` / `admin`
- deschide dashboard-ul `NoteFlow FastAPI Monitoring`

## Oprire si curatare

Sterge toate resursele NoteFlow:

```bash
kubectl delete namespace noteflow
```

Aceasta comanda sterge si volumele persistente create in namespace pentru demo-ul local.
