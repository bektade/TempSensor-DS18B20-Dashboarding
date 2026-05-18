# GrafanaDashboard — live MQTT stack

Docker stack for **live** temperature visualization:

**MQTT (Mosquitto)** → **Telegraf** → **InfluxDB** → **Grafana**

## Folder layout

```
GrafanaDashboard/
├── docker-compose.yml
├── .env.example
├── mqtt_temperature_publisher.py   # run on the Pi (publishes readings)
├── requirements.txt
├── mosquitto/config/
├── telegraf/
└── grafana/provisioning/
```

## Prerequisites

- Docker and Docker Compose on the Pi (or another host on the same network)
- DS18B20 logger sensors configured in `ETL/Extract/ds18b20_sensor_logger.py` (`SENSOR_MAP`)
- Python venv with `paho-mqtt` for the publisher

## Install Docker on Raspberry Pi

If `docker` is not found, install it once (Debian / Raspberry Pi OS):

```bash
cd GrafanaDashboard
chmod +x install-docker.sh
sudo ./install-docker.sh
```

Then **log out and back in** (or reboot) so your user can run Docker without `sudo`.

Check:

```bash
docker --version
docker compose version
```

Manual install (same packages):

```bash
sudo apt-get update
sudo apt-get install -y docker.io docker-compose-plugin
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
```

## 1. Configure secrets

```bash
cd GrafanaDashboard
cp .env.example .env
```

Edit `.env` and set passwords/tokens. Use the **same** `INFLUXDB_ADMIN_TOKEN` value in:

- `.env`
- `grafana/provisioning/datasources/influxdb.yml` → `secureJsonData.token`

## 2. Start the stack

```bash
docker compose up -d
```

| Service   | URL / port        |
|-----------|-------------------|
| Grafana   | http://localhost:3000 |
| InfluxDB  | http://localhost:8086 |
| MQTT      | `localhost:1883`  |

Default Grafana login comes from `.env` (`GRAFANA_ADMIN_USER` / `GRAFANA_ADMIN_PASSWORD`).

Provisioned dashboard: **TempSensor → TempSensor Live** (auto-refresh every 5s).

## 3. Publish sensor readings to MQTT

On the Raspberry Pi (with 1-Wire sensors attached):

```bash
source ../EnvironmentSetup/activate_venv.sh
pip install -r GrafanaDashboard/requirements.txt
python3 GrafanaDashboard/mqtt_temperature_publisher.py
```

Optional environment overrides (see `.env.example`):

- `MQTT_HOST` (default `localhost`)
- `MQTT_PORT` (default `1883`)
- `MQTT_TOPIC` (default `tempsensor/readings`)

### MQTT payload (JSON)

Topic: `tempsensor/readings`

```json
{
  "timestamp": "2026-05-17 17:34:28.856840",
  "sensor_id": "28-0000004a6df4",
  "sensor_label": "Sensor1",
  "temperature_c": 26.062,
  "temperature_f": 78.912
}
```

Telegraf writes these to InfluxDB measurement `sensor_reading` with tags `sensor_id` and `sensor_label`.

## 4. Verify data flow

```bash
# MQTT messages (install mosquitto clients if needed)
mosquitto_sub -h localhost -t 'tempsensor/readings' -v

# Container status
docker compose ps
docker compose logs -f telegraf
```

In Grafana, open **TempSensor Live** and set the time range to **Last 15 minutes** (or **Last 30 minutes**).

## Stop / reset

```bash
docker compose down
# Remove persisted data (clears InfluxDB + Grafana):
docker compose down -v
```

## Notes

- The CSV logger (`ETL/Extract/ds18b20_sensor_logger.py`) and this MQTT publisher can run together; both use the same `SENSOR_MAP` and 30-second interval.
- If Grafana shows “no data”, confirm the InfluxDB token in the datasource YAML matches `.env`, and that the publisher is running while the stack is up.
