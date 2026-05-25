# SensorDataCollector

Real-time **DS18B20** temperatures on a Raspberry Pi: **MQTT → InfluxDB → Grafana**, with every reading saved to CSV.

## Data flow

```
DS18B20  →  mqtt-publisher  →  MQTT  →  Telegraf  →  InfluxDB  →  Grafana
                    └→  exports/YYYY-MM-DD_HHMMAM_TestUnit_serialNumber.csv
```

![Live dashboard](docs/Plot5.png)

---

## Quick start

```bash
cd SensorDataCollector
cp .env.example .env          # first time — set secrets
make startReadSensor          # prompts for TestUnit + serial number
```

- Grafana: http://localhost:3000
- Stop + plot PNG: `make stopReadSensor`
- All targets: `make help`

---

## Project layout

```
SensorDataCollector/
├── Makefile
├── docker-compose.yml
├── publisher/          # sensor read + MQTT + CSV
├── stack/              # Mosquitto, Telegraf, Grafana configs
├── Visualize/          # Plotly PNG charts
├── exports/            # active CSV + archive/
├── scripts/
├── docker/             # mqtt-collector Docker image
└── docs/
```

Long-term test storage is in the sibling **[WebApp](../WebApp/)** stack.

---

## Configuration

| Variable | Purpose |
|----------|---------|
| `INFLUXDB_*` | InfluxDB — [docs/INFLUXDB.md](docs/INFLUXDB.md) |
| `GRAFANA_ADMIN_*` | Grafana login |
| `SAMPLE_INTERVAL` | Seconds between reads (default `60`) |
| `TEST_UNIT`, `SERIAL_NUMBER` | CSV/PNG filename labels |
| `TZ` | Default `America/Chicago` — [docs/TIMEZONE.md](docs/TIMEZONE.md) |

Edit sensors in `publisher/sensor/ds18b20_reader.py` (`SENSOR_MAP`).  
1-Wire setup: [docs/ADDING_SENSORS.md](docs/ADDING_SENSORS.md)

---

## CSV output

Each run creates a file under `exports/`, e.g. `2026-05-18_936PM_Pro18.1_73216-0098.csv`.

On start, existing CSVs in `exports/` move to `exports/archive/`.

Copy finished CSVs to WebApp:

```bash
cp exports/*.csv ../WebApp/data/import_pending/
cd ../WebApp && make import
```

---

## Documentation

| Guide | Contents |
|-------|----------|
| [docs/ADDING_SENSORS.md](docs/ADDING_SENSORS.md) | Add DS18B20 sensors |
| [docs/TIMEZONE.md](docs/TIMEZONE.md) | Timezone and NTP |
| [docs/INFLUXDB.md](docs/INFLUXDB.md) | InfluxDB queries and cleanup |
| [docs/CUSTOM_VISUALIZER.md](docs/CUSTOM_VISUALIZER.md) | Plotly PNG from CSV |
| [docs/DOCKER_HUB.md](docs/DOCKER_HUB.md) | Publish/pull collector image |
| [docs/CI_CD.md](../docs/CI_CD.md) | GitHub Actions auto-publish to Docker Hub |
| [../WebApp/README.md](../WebApp/README.md) | Product test database |

---

## Makefile targets

| Command | Action |
|---------|--------|
| `make env` | Create `.env` from `.env.example` |
| `make startReadSensor` | Prompt TestUnit/serial + start stack |
| `make stopReadSensor` | Stop stack + plot latest CSV (PNG) |
| `make plot` | Plot latest CSV (host venv) |
| `make check` | Verify MQTT, CSV, Influx pipeline |
| `make clean-influx` | Delete InfluxDB data |
| `make docker-publish-collector` | Build + push Hub image |
