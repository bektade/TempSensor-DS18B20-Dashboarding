# CI/CD — Docker Hub publish

Two **separate** workflows on branch **`djangoWebApp`** (repo default branch).

| Image | Docker Hub | Workflow |
|-------|------------|----------|
| WebApp | `becktkh/tempsensor-webapp` | [docker-publish-webapp.yml](../.github/workflows/docker-publish-webapp.yml) |
| SensorDataCollector | `becktkh/tempsensor-mqtt-collector` | [docker-publish-collector.yml](../.github/workflows/docker-publish-collector.yml) |

GitHub **Actions** tab:

- **Docker Hub — WebApp**
- **Docker Hub — SensorDataCollector**

---

## One-time setup (GitHub)

### 1. Docker Hub access token

[hub.docker.com](https://hub.docker.com) → **Account Settings → Security → New Access Token** (Read & Write).

### 2. Repository secrets

**Settings → Secrets and variables → Actions**

| Secret | Value |
|--------|--------|
| `DOCKERHUB_USERNAME` | e.g. `becktkh` |
| `DOCKERHUB_TOKEN` | Your token |

### 3. Default branch

Confirm **Settings → General → Default branch** is **`djangoWebApp`**.  
Both workflows only listen to that branch (plus release tags below).

---

## WebApp workflow

**Runs on `djangoWebApp` when:**

| Trigger | Publishes? |
|---------|------------|
| Push with changes under `WebApp/**` | Yes → `latest`, `djangoWebApp`, commit SHA |
| Git tag `webapp-v1.0.0` (any branch) | Yes → Docker tag `1.0.0` |
| Pull request **into** `djangoWebApp` | Build only |
| **Run workflow** → branch `djangoWebApp` | Yes |

Does **not** run for pushes that only touch `SensorDataCollector/`.

### Release WebApp

```bash
git checkout djangoWebApp
git pull
git tag webapp-v1.0.0
git push origin webapp-v1.0.0
```

Deploy on Pi:

```bash
cd WebApp
# .env: DOCKER_TAG=latest   (or 1.0.0 for a release tag)
make rebuildwebapp-hub
```

---

## SensorDataCollector workflow

**Runs on `djangoWebApp` when:**

| Trigger | Publishes? |
|---------|------------|
| Push with changes under `SensorDataCollector/**` | Yes → `latest`, `djangoWebApp`, commit SHA |
| Git tag `collector-v1.0.0` | Yes → Docker tag `1.0.0` |
| Pull request **into** `djangoWebApp` | Build only |
| **Run workflow** → branch `djangoWebApp` | Yes |

Does **not** run for pushes that only touch `WebApp/`.

### Release collector

```bash
git checkout djangoWebApp
git pull
git tag collector-v1.0.0
git push origin collector-v1.0.0
```

Deploy on Pi:

```bash
cd SensorDataCollector
# .env: DOCKER_TAG=latest   (or 1.0.0)
make startReadSensor
```

---

## Docker tags on each push to `djangoWebApp`

| Tag | Meaning |
|-----|---------|
| `latest` | Newest build from `djangoWebApp` |
| `djangoWebApp` | Same branch name tag |
| short SHA | e.g. `a1b2c3d` |

Use on devices:

```
DOCKER_TAG=latest
```

---

## Manual run (one image at a time)

1. **Actions** → pick **Docker Hub — WebApp** or **Docker Hub — SensorDataCollector**
2. **Run workflow**
3. Branch: **`djangoWebApp`**
4. **Run workflow**

---

## Manual publish (local)

```bash
cd WebApp && export DOCKERHUB_USER=becktkh DOCKER_TAG=my-tag && make docker-publish
```

```bash
cd SensorDataCollector && export DOCKERHUB_USER=becktkh DOCKER_TAG=my-tag && make docker-publish-collector
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Workflow did not start | Push must be on **`djangoWebApp`** and touch that component’s folder (or run workflow manually) |
| No `latest` tag | Only pushes to **`djangoWebApp`** get `latest`; check branch name |
| `denied: requested access` | Fix `DOCKERHUB_USERNAME` / `DOCKERHUB_TOKEN` secrets |
| Pi still old image | `DOCKER_TAG=latest` in the right `.env`, then rebuild that stack only |

---

## Related docs

- [WebApp/docs/DOCKER_HUB.md](../WebApp/docs/DOCKER_HUB.md)
- [SensorDataCollector/docs/DOCKER_HUB.md](../SensorDataCollector/docs/DOCKER_HUB.md)
- [WebApp/docs/DATABASE_BACKUP.md](../WebApp/docs/DATABASE_BACKUP.md)
