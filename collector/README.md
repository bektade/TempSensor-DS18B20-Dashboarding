# Docker Hub — MQTT / Grafana sensor data collector

Pre-built image for **mqtt-publisher**: DS18B20 → MQTT + CSV export.

**Repository:** `becktkh/tempsensor-mqtt-collector`

```
DS18B20 → mqtt-publisher (this image) → MQTT → Telegraf → InfluxDB → Grafana
```

---

## Push next time

Replace `tagname` with your tag (`latest`, `v1.0.0`, etc.).

```bash
docker login

cd ~/Projects/TempSensor
docker build -f collector/Dockerfile -t becktkh/tempsensor-mqtt-collector:tagname .
docker push becktkh/tempsensor-mqtt-collector:tagname
```

**Make shortcut:**

```bash
export DOCKERHUB_USER=becktkh
export DOCKER_TAG=tagname
cd ~/Projects/TempSensor
make docker-publish-collector
```

---

## Pull and run

```bash
cd ~/Projects/TempSensor
export DOCKER_IMAGE_COLLECTOR=becktkh/tempsensor-mqtt-collector
export DOCKER_TAG=tagname

docker compose -f docker-compose.yml -f docker-compose.hub.yml up -d --no-build mqtt-publisher
```

Add to repo root `.env`:

```
DOCKERHUB_USER=becktkh
DOCKER_IMAGE_COLLECTOR=becktkh/tempsensor-mqtt-collector
DOCKER_TAG=latest
```

---

## Host requirements

- 1-Wire enabled (`/sys/bus/w1/devices` mounted into container)
- `TEST_UNIT` and `SERIAL_NUMBER` in `.env`
- `publisher/sensor/ds18b20_reader.py` `SENSOR_MAP` configured before build

Full guide: [../docs/DOCKER_HUB.md](../docs/DOCKER_HUB.md)
