# Docker Hub — WebApp

Image: **`becktkh/tempsensor-webapp`** (tag from `DOCKER_TAG` in `.env`)

---

## First time (Pi, Mac, or any machine)

```bash
cd WebApp
cp .env.example .env          # set passwords; DOCKER_TAG=latest
make startwebapp-hub
```

Open http://localhost:8000/

---

## Pull a new image / rebuild from Hub

Edit `.env` if the tag changed (`DOCKER_TAG=v1.0.0`), then:

```bash
cd WebApp
make rebuildwebapp-hub
```

Database data is kept (Postgres volume). To move to another machine, backup first — see [DATABASE_BACKUP.md](DATABASE_BACKUP.md).

---

## Stop

```bash
make stopWebApp
```

---

## Publish new image

**Automatic:** push changes under `WebApp/` or tag `webapp-v1.0.0` — workflow **Docker Hub — WebApp** — see [CI/CD](../../docs/CI_CD.md).

**Manual:**

```bash
cd WebApp
export DOCKERHUB_USER=becktkh
export DOCKER_TAG=tagname
make docker-publish
```

---

## `.env` (minimum)

```
POSTGRES_PASSWORD=...
DJANGO_SECRET_KEY=...
DJANGO_SUPERUSER_PASSWORD=...
DOCKER_IMAGE_WEBAPP=becktkh/tempsensor-webapp
DOCKER_TAG=latest
```

More: [TROUBLESHOOTING.md](TROUBLESHOOTING.md) · [CI/CD](../../docs/CI_CD.md) · Collector: [../../SensorDataCollector/docs/DOCKER_HUB.md](../../SensorDataCollector/docs/DOCKER_HUB.md)
