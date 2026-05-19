# TempSensor — Grafana live stack

Real-time **DS18B20** temperatures on a Raspberry Pi: **MQTT → InfluxDB → Grafana**, with every reading also saved to CSV.

```
DS18B20  →  mqtt-publisher  →  MQTT  →  Telegraf  →  InfluxDB  →  Grafana
                    └→  exports/temp_reading_YYYY-MM-DD_HMMAM.csv
```

**License:** [MIT](LICENSE) — free to use, modify, and share with attribution.

**Author:** [Bek Kobro](https://bekcsys.com/about) — Automation Engineer

---

## Run

From the project root: `cd ~/Projects/TempSensor`

### 1. Check 1-Wire

```bash
ls /sys/bus/w1/devices/28-*
```

If empty: enable 1-Wire in `sudo raspi-config`, reboot — see [docs/ADDING_SENSORS.md](docs/ADDING_SENSORS.md).

### 2. Configure sensors

Edit `publisher/sensor/ds18b20_reader.py` — set `SENSOR_MAP`.

### 3. Secrets

```bash
cp .env.example .env
nano .env
```

### 4. Timezone (Chicago / CDT)

If timestamps look 5 hours ahead (UTC instead of local), set the Pi and stack to Chicago time:

```bash
sudo ./scripts/setup_timezone.sh
```

Add `TZ=America/Chicago` to `.env` if it is not there, then:

```bash
docker compose up -d --force-recreate mqtt-publisher grafana
```

### 5. Start the stack

```bash
docker compose up -d --build
```

### 6. Open Grafana

http://localhost:3000 → login from `.env` → **Dashboards → TempSensor → TempSensor Live**

```bash
tail -f exports/temp_reading_*.csv
docker compose logs mqtt-publisher --tail 5
```

---

## Project structure

```
TempSensor/
├── README.md
├── LICENSE
├── AUTHORS.md
├── docker-compose.yml
├── publisher/              # sensor read + MQTT + CSV
├── stack/                  # Mosquitto, Telegraf, Grafana
├── scripts/
├── Visualize/              # matplotlib plot from latest CSV
├── docs/ADDING_SENSORS.md
└── exports/                # active CSV + archive/ (gitignored)
```

---

## Configuration (`.env`)

| Variable | Purpose |
|----------|---------|
| `INFLUXDB_*` | InfluxDB setup + token |
| `GRAFANA_ADMIN_*` | Grafana login |
| `MQTT_TOPIC` | Default `tempsensor/readings` |
| `SAMPLE_INTERVAL` | Seconds between reads and CSV rows (default `60`, one per minute) |
| `CSV_DIR` | Directory for per-run CSV files (default `exports`) |
| `TZ` | Default `America/Chicago` (CSV + Grafana local time) |

---

## CSV log

Each time the publisher starts, it creates a new file under `exports/`, for example
`temp_reading_2026-05-18_936PM.csv` (9:36 PM on 18 May 2026).

On `docker compose up`, any CSV files in `exports/` are moved to `exports/archive/` before a new run file is created.

On `docker compose down`, the latest CSV stays in `exports/`; a matching PNG is written to `Visualize/output/`.

Columns: `timestamp`, `sensor_id`, `sensor_label`, `temperature_c`, `temperature_f`

---

## Clean database (keep CSV)

To wipe InfluxDB so Grafana starts fresh **without** deleting the CSV archive:

```bash
./scripts/clean_influx_data.sh
```

Confirm with `y`, or pass `-y` to skip the prompt. Optional: delete only Telegraf’s measurement:

```bash
./scripts/clean_influx_data.sh -y --measurement sensor_reading
```

The stack keeps running; new readings are written to Influx and appended to the CSV as usual.

---

## Custom plot (PNG on `docker compose down`)

When you stop the stack, the publisher **stops reading** and saves a **presentation PNG** (Plotly: shared 90‑min axis, °C and °F subplots) named like the CSV (same basename, `.png` instead of `.csv`). The CSV is **not** archived on down—only on the next `docker compose up`.

**Recommended on the Pi** (plots on the host — most reliable):

```bash
./scripts/compose-down.sh
```

Or plain `docker compose down` (plots inside the mqtt-publisher container after rebuild).

```bash
# exports/temp_reading_2026-05-18_936PM.csv  (kept)
# Visualize/output/temp_reading_2026-05-18_936PM.png
```

Grafana is unchanged; this is an extra chart for slides and reports.

Manual plot (optional):

```bash
./scripts/plot_latest_csv.sh --presentation --output-auto
```

---

## Grafana dashboard

- Auto-built from `stack/grafana/dashboards/tempsensor-live.template.json`
- Customize in the UI → **Save dashboard** (stored in `grafana_data` volume)
- Reset layout: `docker compose down -v && docker compose up -d --build`

---

## Scripts

| Script | Use |
|--------|-----|
| `scripts/install-docker.sh` | Install Docker on Pi (`sudo`) |
| `scripts/check_pipeline.sh` | Test MQTT, CSV, Influx |
| `scripts/clean_influx_data.sh` | Erase InfluxDB data; keep CSV |
| `scripts/setup_timezone.sh` | Pi NTP + `America/Chicago` (sudo) |
| `scripts/firstTimeSetup.sh` | Optional host Python venv |
| `scripts/compose-down.sh` | Stop stack + plot latest CSV (recommended) |
| `scripts/plot_latest_csv.sh` | Manual Plotly PNG from latest CSV |

---

## Documentation

| Guide | Contents |
|-------|----------|
| [docs/ADDING_SENSORS.md](docs/ADDING_SENSORS.md) | Add DS18B20 sensors |
| [AUTHORS.md](AUTHORS.md) | Author information |

---

## License

Released under the [MIT License](LICENSE). You may use, copy, modify, and distribute this software for any purpose, including commercial use, provided the copyright notice and license text are included.

Copyright (c) 2026 [Bek Kobro](https://bekcsys.com/about).

---

## Do not commit

`.env`, `venv/`, `exports/*.csv`, `TempSensor Live-*.json`
