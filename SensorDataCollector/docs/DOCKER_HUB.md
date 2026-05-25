# Docker Hub — SensorDataCollector

Image: **`becktkh/tempsensor-mqtt-collector`** (tag from `DOCKER_TAG` in `.env`)

---

## Publish

**Automatic:** push changes under `SensorDataCollector/` or tag `collector-v1.0.0` — workflow **Docker Hub — SensorDataCollector** — see [CI/CD](../../docs/CI_CD.md).

**Manual:**

```bash
cd SensorDataCollector
export DOCKERHUB_USER=becktkh
export DOCKER_TAG=tagname
make docker-publish-collector
```

Details: [docker/README.md](../docker/README.md)

---

## Pull pre-built image

Set in `.env`:

```
DOCKER_IMAGE_COLLECTOR=becktkh/tempsensor-mqtt-collector
DOCKER_TAG=latest
```

Then start the stack as usual (`make startReadSensor`). The compose hub override pulls the image instead of building locally.

WebApp image: [../../WebApp/docs/DOCKER_HUB.md](../../WebApp/docs/DOCKER_HUB.md) · CI/CD: [../../docs/CI_CD.md](../../docs/CI_CD.md)
