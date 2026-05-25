# Docker Hub — Product Test Data WebApp

Use the pre-built Django image **`becktkh/tempsensor-webapp`** instead of building locally.

| Component | Source |
|-----------|--------|
| **django_web** | Docker Hub — `becktkh/tempsensor-webapp:tagname` |
| **postgres** | Official image — `postgres:16-alpine` (same compose file) |
| **pgAdmin** | Optional — [pgadmin/README.md](../pgadmin/README.md) |

---

## Setup on another machine (Mac, Windows, or Linux PC)

Run the full WebApp stack on a **new computer** by pulling the published image. No Python or venv required — only Docker.

Typical use: develop or browse test data on a **MacBook** while the Raspberry Pi runs the sensor stack, or stand up a copy of the database UI on your desk machine.

### Prerequisites

1. **Docker Desktop** installed and running  
   - Mac: [Docker Desktop for Mac](https://docs.docker.com/desktop/setup/install/mac-install/)  
   - Windows: Docker Desktop for Windows  
   - Linux: Docker Engine + Compose plugin  

2. **Git** (recommended) or a copy of the `WebApp/` folder  

3. Internet access to pull from Docker Hub  

Verify:

```bash
docker --version
docker compose version
```

### Step 1 — Get the WebApp files

**Option A — Clone the repo (recommended)**

```bash
git clone <your-repo-url> TempSensor
cd TempSensor/WebApp
```

**Option B — Copy only `WebApp/`**

Copy the whole `WebApp` directory from the Pi or another machine (USB, scp, zip). You need at minimum:

```
WebApp/
├── docker-compose.yml
├── docker-compose.hub.yml
├── .env.example
├── Makefile          # optional but helpful
└── data/             # create empty dirs if missing
```

### Step 2 — Configure environment

```bash
cd WebApp
cp .env.example .env
```

Edit `.env` on Mac:

```bash
open -e .env          # TextEdit
# or: nano .env  /  code .env
```

**Required settings:**

```bash
# Database (used by postgres + django containers)
POSTGRES_DB=sauna_tests
POSTGRES_USER=sauna_user
POSTGRES_PASSWORD=choose_a_strong_password

# Django
DJANGO_SECRET_KEY=long-random-string-at-least-50-chars
DJANGO_DEBUG=1
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=choose_admin_password

# Docker Hub image to pull
DOCKERHUB_USER=becktkh
DOCKER_IMAGE_WEBAPP=becktkh/tempsensor-webapp
DOCKER_TAG=latest
```

Create data folders for CSV import:

```bash
mkdir -p data/import_pending data/archive/db_migrated data/archive/import_failed data/logs
```

### Step 3 — Pull and start

**With Make** (if installed — Mac often has it via Xcode tools):

```bash
make startwebapp-hub
```

**Without Make** (works everywhere):

```bash
docker compose -f docker-compose.yml -f docker-compose.hub.yml pull django_web
docker compose -f docker-compose.yml -f docker-compose.hub.yml up -d --no-build
```

First start takes a minute. The container will:

- Apply database migrations  
- Collect admin static files  
- Create the Django superuser from `.env` (if new database)  

### Step 4 — Open the app on your Mac

| URL | Purpose |
|-----|---------|
| http://localhost:8000/ | Dashboard |
| http://localhost:8000/admin/ | Django admin (`admin` + password from `.env`) |

Postgres is exposed on the Mac at **localhost:5433** (for pgAdmin or `psql`).

### Step 5 — Import CSV (optional)

```bash
cp /path/to/exports/*.csv data/import_pending/
make import
```

Without Make:

```bash
docker compose exec django_web python manage.py import_pending_csv
```

See [CSV_IMPORT.md](CSV_IMPORT.md).

### Step 6 — Optional pgAdmin on Mac

Database browser in a separate stack:

```bash
cd pgadmin
make start
```

Open http://localhost:5050/ — see [pgadmin/README.md](../pgadmin/README.md).  
pgAdmin connects to Postgres at `host.docker.internal:5433`.

### Stop / restart on Mac

```bash
make stopWebApp
# or:
docker compose -f docker-compose.yml -f docker-compose.hub.yml down
```

Start again:

```bash
make startwebapp-hub
```

---

## Mac vs Raspberry Pi — two common setups

| Scenario | Where Docker runs | Browser URL |
|----------|-------------------|-------------|
| **A. WebApp on your Mac** | Mac (this guide) | http://localhost:8000/ |
| **B. WebApp on the Pi, browse from Mac** | Raspberry Pi only | http://\<pi-ip\>:8000/ (not localhost) |

**Scenario A** — follow the steps above on the Mac; data lives in Docker volumes on the Mac.

**Scenario B** — do not run WebApp on the Mac; on the Pi run `make startwebapp-hub` (or `startwebapp`), then on the Mac open `http://192.168.x.x:8000/` where `x.x` is the Pi’s LAN address (`hostname -I` on the Pi).

---

## Apple Silicon (M1/M2/M3 Mac)

Docker Desktop runs **linux/arm64** containers natively. Use a Hub tag built for arm64, or a multi-arch tag:

```bash
docker pull becktkh/tempsensor-webapp:latest
docker image inspect becktkh/tempsensor-webapp:latest --format '{{.Architecture}}'
```

If the image is amd64-only, Docker Desktop still runs it via emulation (slower but usually fine). For best performance on Pi **and** Mac, publish multi-arch images (see [Publish](#publish-a-new-image-maintainers)).

---

## Update to a new image tag

```bash
cd WebApp
# Edit .env: DOCKER_TAG=v1.0.1

docker compose -f docker-compose.yml -f docker-compose.hub.yml pull django_web
docker compose -f docker-compose.yml -f docker-compose.hub.yml up -d --no-build django_web
```

Or: `export DOCKER_TAG=v1.0.1 && make startwebapp-hub`

---

## Run from image vs build locally

| | **Docker Hub** (`startwebapp-hub`) | **Local build** (`startwebapp`) |
|---|-----------------------------------|--------------------------------|
| Mac / Pi speed | Fast — pull only | Slow — installs Python deps |
| Command | `make startwebapp-hub` | `make startwebapp` |
| Compose files | `docker-compose.yml` + `docker-compose.hub.yml` | `docker-compose.yml` only |
| Use when | New machine setup, production-like deploy | Changing app source code |

---

## Troubleshooting (Mac and other hosts)

| Problem | Fix |
|---------|-----|
| `Cannot connect to Docker daemon` | Start **Docker Desktop**; wait until the whale icon is ready |
| `pull access denied` | Public images need no login; for private repos run `docker login` |
| Port 8000 already in use | Set `DJANGO_PUBLISH_PORT=8001` in `.env`, restart compose |
| Port 5433 already in use | Set `POSTGRES_PUBLISH_PORT=5434` in `.env` |
| Admin login fails | Use credentials from `.env`; run `make resetadmin` on the same machine |
| **403 Forbidden** on admin | Open the same host you used at start (`localhost`, not mixed with IP) |
| Empty database | Normal on first run — import CSV or add data in `/admin/` |
| `make: command not found` | Use the `docker compose` commands in Step 3 instead |

More: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## Publish a new image (maintainers)

Replace `tagname` with your tag (`latest`, `v1.0.0`, etc.).

```bash
docker login

cd WebApp
docker build -t becktkh/tempsensor-webapp:tagname .
docker push becktkh/tempsensor-webapp:tagname
```

**Make shortcut:**

```bash
export DOCKERHUB_USER=becktkh
export DOCKER_TAG=tagname
make docker-publish
```

### Multi-arch (Raspberry Pi arm64 + Mac/PC amd64)

```bash
cd WebApp
docker buildx create --use
docker buildx build --platform linux/amd64,linux/arm64 \
  -t becktkh/tempsensor-webapp:tagname --push .
```

Both images overview: [../docs/DOCKER_HUB.md](../docs/DOCKER_HUB.md)
