# TempSensor — Grafana live stack

Raspberry Pi DS18B20 readings streamed in real time:

**DS18B20** → **MQTT (Mosquitto)** → **Telegraf** → **InfluxDB** → **Grafana**

No CSV files or Flask visualizer on this branch — sensors are read directly from `/sys/bus/w1/devices/`.

## Layout

```
TempSensor/
├── sensor/ds18b20_reader.py   # 1-Wire read + SENSOR_MAP
├── mqtt_publisher.py          # publish readings to MQTT
├── docker-compose.yml         # Mosquitto, Telegraf, InfluxDB, Grafana
├── telegraf/                  # MQTT → InfluxDB
├── grafana/provisioning/      # datasource + TempSensor Live dashboard
├── mosquitto/config/
├── .env.example
├── install-docker.sh
└── requirements.txt           # paho-mqtt (publisher only)
```

## Prerequisites

- Raspberry Pi with 1-Wire enabled and DS18B20 visible under `/sys/bus/w1/devices/`
- Docker and Docker Compose (`sudo ./install-docker.sh`, then log out/in)
- Python 3 venv for the MQTT publisher on the Pi

## 1. Configure sensors

Edit `sensor/ds18b20_reader.py` — set `SENSOR_MAP` to your device IDs and labels:

```python
SENSOR_MAP = {
    '28-0000004a6df4': 'Sensor1',
}
```

Optional: test reads without Docker:

```bash
python3 sensor/ds18b20_reader.py
```

## 2. Python environment (publisher)

```bash
./firstTimeSetup.sh
source activate_venv.sh
```

## 3. Secrets and Docker stack

```bash
cp .env.example .env
# Edit .env — set passwords and INFLUXDB_ADMIN_TOKEN
# Use the SAME token in grafana/provisioning/datasources/influxdb.yml
docker compose up -d
```

| Service  | URL |
|----------|-----|
| Grafana  | http://localhost:3000 |
| InfluxDB | http://localhost:8086 |
| MQTT     | localhost:1883 |

Login: `GRAFANA_ADMIN_USER` / `GRAFANA_ADMIN_PASSWORD` from `.env`.

Dashboard: **Dashboards → TempSensor Live** (auto-refresh 5s).

## 4. Start live publishing

With the stack running:

```bash
source activate_venv.sh
python3 mqtt_publisher.py
```

Environment overrides (or add to `.env` and export before running):

- `MQTT_HOST` (default `localhost`)
- `MQTT_PORT` (default `1883`)
- `MQTT_TOPIC` (default `tempsensor/readings`)
- `SAMPLE_INTERVAL` (default `30` seconds)

## Verify

```bash
docker compose ps
mosquitto_sub -h localhost -t 'tempsensor/readings' -v
docker compose logs -f telegraf
```

## Stop / reset

```bash
docker compose down
docker compose down -v   # also deletes InfluxDB + Grafana data
```

## Branch note

The **master** branch keeps CSV logging and the Flask/Plotly visualizer. This **Grafana** branch is MQTT/InfluxDB/Grafana only.
