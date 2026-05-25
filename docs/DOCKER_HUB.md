# Docker Hub images

Published images for this project (Docker Hub user **`becktkh`**):

| Image | Repository |
|-------|----------------|
| WebApp (Django) | `becktkh/tempsensor-webapp` |
| MQTT sensor collector | `becktkh/tempsensor-mqtt-collector` |

Infrastructure (Postgres, Mosquitto, InfluxDB, Telegraf, Grafana) uses official images — not published to Hub.

**Setup on a new machine (Mac, PC, Linux):** [WebApp/docs/DOCKER_HUB.md](../WebApp/docs/DOCKER_HUB.md#setup-on-another-machine-mac-windows-or-linux-pc) — pull `becktkh/tempsensor-webapp` and run Postgres + Django without building.

---

## Push next time (cheat sheet)

Replace `tagname` with your tag (e.g. `latest`, `v1.0.0`, `2026-05-25`).

```bash
docker login
```

**Build, tag, and push — WebApp:**

```bash
cd WebApp
docker build -t becktkh/tempsensor-webapp:tagname .
docker push becktkh/tempsensor-webapp:tagname
```

**Build, tag, and push — MQTT collector:**

```bash
cd ~/Projects/TempSensor
docker build -f collector/Dockerfile -t becktkh/tempsensor-mqtt-collector:tagname .
docker push becktkh/tempsensor-mqtt-collector:tagname
```

**Or use Make** (sets `DOCKERHUB_USER=becktkh` and tag from `DOCKER_TAG`):

```bash
export DOCKERHUB_USER=becktkh
export DOCKER_TAG=tagname

cd WebApp && make docker-publish
cd ~/Projects/TempSensor && make docker-publish-collector
```

---

## Pull and run

### WebApp (any machine — Pi, Mac, PC)

Full walkthrough: [WebApp/docs/DOCKER_HUB.md](../WebApp/docs/DOCKER_HUB.md#setup-on-another-machine-mac-windows-or-linux-pc)

```bash
git clone <repo-url> TempSensor
cd TempSensor/WebApp
cp .env.example .env    # edit passwords + DOCKER_TAG
mkdir -p data/import_pending data/archive/db_migrated data/archive/import_failed

docker compose -f docker-compose.yml -f docker-compose.hub.yml pull django_web
docker compose -f docker-compose.yml -f docker-compose.hub.yml up -d --no-build
```

Open http://localhost:8000/ on that machine.

### MQTT collector (Grafana stack)

```bash
cd ~/Projects/TempSensor
export DOCKER_IMAGE_COLLECTOR=becktkh/tempsensor-mqtt-collector
export DOCKER_TAG=tagname

docker compose -f docker-compose.yml -f docker-compose.hub.yml up -d --no-build mqtt-publisher
```

---

## Environment variables (`.env`)

**WebApp/.env** or repo root `.env`:

```
DOCKERHUB_USER=becktkh
DOCKER_IMAGE_WEBAPP=becktkh/tempsensor-webapp
DOCKER_IMAGE_COLLECTOR=becktkh/tempsensor-mqtt-collector
DOCKER_TAG=latest
```

---

## Raspberry Pi (arm64)

```bash
# WebApp
cd WebApp
docker buildx build --platform linux/arm64 \
  -t becktkh/tempsensor-webapp:tagname --push .

# Collector
cd ~/Projects/TempSensor
docker buildx build --platform linux/arm64 -f collector/Dockerfile \
  -t becktkh/tempsensor-mqtt-collector:tagname --push .
```

---

## More detail

- WebApp: [WebApp/docs/DOCKER_HUB.md](../WebApp/docs/DOCKER_HUB.md)
- MQTT collector: [collector/README.md](../collector/README.md)
