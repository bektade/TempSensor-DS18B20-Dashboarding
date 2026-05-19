# TempSensor Logging and Viz ( MQTT+Grafana )

Real-time **DS18B20** temperatures on a Raspberry Pi: **MQTT → InfluxDB → Grafana**, with every reading also saved to CSV.

### Data flow : 
```
DS18B20  →  mqtt-publisher  →  MQTT  →  Telegraf  →  InfluxDB  →  Grafana
                    └→  exports/temp_reading_YYYY-MM-DD_HMMAM.csv

```


### Project structure

```
TempSensor/
├── README.md
├── LICENSE
├── AUTHORS.md
├── docker-compose.yml
├── publisher/              # sensor read + MQTT + CSV
├── stack/                  # Mosquitto, Telegraf, Grafana
├── scripts/
├── Visualize/              # Plotly PNG — see docs/CUSTOM_VISUALIZER.md
├── docs/
└── exports/                # active CSV + archive/ (gitignored)
```

---

# How to run

From the project root: `cd ~/Projects/TempSensor`

#### 1. Check 1-Wire

```bash
ls /sys/bus/w1/devices/28-*
```

If empty: enable 1-Wire in `sudo raspi-config`, reboot — see [docs/ADDING_SENSORS.md](docs/ADDING_SENSORS.md).

#### 2. Configure sensors

Edit `publisher/sensor/ds18b20_reader.py` — set `SENSOR_MAP`.

#### 3. Secrets

```bash
cp .env.example .env
nano .env
```

Timezone wrong (UTC vs Chicago)? See [docs/TIMEZONE.md](docs/TIMEZONE.md).

#### 4. Start the stack

```bash
docker compose up -d --build
```

#### 5. Open Grafana

http://localhost:3000 → login from `.env` → **Dashboards → TempSensor → TempSensor Live**

```bash
tail -f exports/temp_reading_*.csv
docker compose logs mqtt-publisher --tail 5
```



---

# Configuration (`.env`)

| Variable | Purpose |
|----------|---------|
| `INFLUXDB_*` | InfluxDB — see [docs/INFLUXDB.md](docs/INFLUXDB.md) |
| `GRAFANA_ADMIN_*` | Grafana login |
| `MQTT_TOPIC` | Default `tempsensor/readings` |
| `SAMPLE_INTERVAL` | Seconds between reads and CSV rows (default `60`, one per minute) |
| `CSV_DIR` | Directory for per-run CSV files (default `exports`) |
| `VISUALIZE_OUTPUT_DIR` | PNG output — see [docs/CUSTOM_VISUALIZER.md](docs/CUSTOM_VISUALIZER.md) |
| `TZ` | Default `America/Chicago` — see [docs/TIMEZONE.md](docs/TIMEZONE.md) |

---

## Data 

Each time the publisher starts, it creates a new file under `exports/`, for example
`temp_reading_2026-05-18_936PM.csv` (9:36 PM on 18 May 2026).

On `docker compose up`, any CSV files in `exports/` are moved to `exports/archive/` before a new run file is created.

Columns: `timestamp`, `sensor_id`, `sensor_label`, `temperature_c`, `temperature_f`

Presentation PNG from the latest CSV: [docs/CUSTOM_VISUALIZER.md](docs/CUSTOM_VISUALIZER.md).

---

# Real-time visualization : Grafana 

- Auto-built from `stack/grafana/dashboards/tempsensor-live.template.json`
- Customize in the UI → **Save dashboard** (stored in `grafana_data` volume)
- Reset layout: `docker compose down -v && docker compose up -d --build`

---

# Automation Scripts

| Script | Use |
|--------|-----|
| `scripts/install-docker.sh` | Install Docker on Pi (`sudo`) |
| `scripts/check_pipeline.sh` | Test MQTT, CSV, Influx |
| `scripts/clean_influx_data.sh` | Erase InfluxDB — see [docs/INFLUXDB.md](docs/INFLUXDB.md) |
| `scripts/setup_timezone.sh` | Pi NTP + `America/Chicago` — see [docs/TIMEZONE.md](docs/TIMEZONE.md) |
| `scripts/firstTimeSetup.sh` | Optional host Python venv |
| `scripts/compose-down.sh` | Stop stack + plot — see [docs/CUSTOM_VISUALIZER.md](docs/CUSTOM_VISUALIZER.md) |
| `scripts/plot_latest_csv.sh` | Refresh PNG — see [docs/CUSTOM_VISUALIZER.md](docs/CUSTOM_VISUALIZER.md) |

---

# Documentation

| Guide | Contents |
|-------|----------|
| [docs/ADDING_SENSORS.md](docs/ADDING_SENSORS.md) | Add DS18B20 sensors |
| [docs/TIMEZONE.md](docs/TIMEZONE.md) | Chicago / CDT timezone and NTP |
| [docs/INFLUXDB.md](docs/INFLUXDB.md) | InfluxDB config, queries, cleanup |
| [docs/CUSTOM_VISUALIZER.md](docs/CUSTOM_VISUALIZER.md) | Plotly PNG charts from CSV |
| [docs/AUTHORS.md](AUTHORS.md) | About the Author |

---

#### Do not commit

`.env`, `venv/`, `exports/*.csv`, `TempSensor Live-*.json`

---

## License and author

Licensed under the [MIT License](LICENSE). You may use, copy, modify, and distribute this software for any purpose, including commercial use, provided the copyright notice and license text are included.

Copyright (c) 2026 [Bek Kobro](https://bekcsys.com/about). See [AUTHORS.md](AUTHORS.md).
