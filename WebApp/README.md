# Product Test Data

PostgreSQL + Django for long-term test storage. Separate from the TempSensor MQTT / Grafana / InfluxDB stack.

## Start

```bash
cd WebApp
cp .env.example .env   # first time only — set passwords and DJANGO_SECRET_KEY
make startwebapp
```

| Command | Action |
|---------|--------|
| `make startwebapp` | Start Postgres + Django (build image locally) |
| `make startwebapp-hub` | Start Postgres + Django (pull `becktkh/tempsensor-webapp` from Docker Hub) |
| `make import` | Import `data/import_pending/*.csv` into PostgreSQL |
| `make migrate` | Run migrations |
| `make stopWebApp` | Stop Postgres + Django |
| `make urls` | Show correct URL (Pi vs PC on the network) |
| `make status` | Check containers are running |
| `make help` | All targets + import steps |

**pgAdmin (optional):** `cd pgadmin && make start` — see [pgadmin/README.md](pgadmin/README.md)

**Connection refused on localhost?** You may be on a PC while the app runs on the Pi — run `make urls`. See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).

**Import CSV:** `cp ../exports/*.csv data/import_pending/` then `make import` (requires `make startwebapp` first).

- On the Pi: http://localhost:8000/
- From another PC on the network: `http://<pi-ip>:8000/` (e.g. `http://192.168.0.198:8000/`) — not `localhost`
- Admin: http://localhost:8000/admin/
- pgAdmin (optional): `cd pgadmin && make start` — [pgadmin/README.md](pgadmin/README.md)

Django admin: http://localhost:8000/admin/ — see [docs/DJANGO_ADMIN.md](docs/DJANGO_ADMIN.md) (forgot password: `make resetadmin`)

## Documentation

| Guide | Contents |
|-------|----------|
| [docs/CSV_IMPORT.md](docs/CSV_IMPORT.md) | Import CSV into the database |
| [docs/DATABASE.md](docs/DATABASE.md) | PostgreSQL access and example queries |
| [docs/DJANGO_ADMIN.md](docs/DJANGO_ADMIN.md) | Django `/admin/` login and password reset |
| [pgadmin/README.md](pgadmin/README.md) | pgAdmin (optional DB browser) |
| [docs/DOCKER_HUB.md](docs/DOCKER_HUB.md) | Run on Mac/PC from Docker Hub or publish tags |
| [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) | Host `.venv`, local `runserver`, superuser |
| [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Connection refused, 400 errors |
