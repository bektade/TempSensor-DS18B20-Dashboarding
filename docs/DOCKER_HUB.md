# Docker Hub

The two docker images rom the tool. WebApp is django based and MQTT collector collects data from sensors. 

| Image | Repository |
|-------|----------------|
| WebApp | `becktkh/tempsensor-webapp` |
| MQTT collector | `becktkh/tempsensor-mqtt-collector` |

---

## WebApp — run from Hub

```bash
cd WebApp
cp .env.example .env
make startwebapp-hub
```

**Rebuild after a new tag:**

```bash
cd WebApp
make rebuildwebapp-hub
```

Full guide: [WebApp/docs/DOCKER_HUB.md](../WebApp/docs/DOCKER_HUB.md)

---

## MQTT collector — publish

```bash
cd ~/Projects/TempSensor
export DOCKERHUB_USER=becktkh
export DOCKER_TAG=tagname
make docker-publish-collector
```

Details: [collector/README.md](../collector/README.md)
