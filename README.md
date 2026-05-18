# TempSensor — Grafana live stack (Raspberry Pi)

```
DS18B20  →  mqtt-publisher  →  MQTT  →  Telegraf  →  InfluxDB  →  Grafana
                    └→  exports/mqtt_readings.csv
```

```bash
cd ~/Projects/TempSensor
cp .env.example .env && nano .env
docker compose up -d --build
```

Grafana: http://localhost:3000 → **TempSensor → TempSensor Live**

**Add more DS18B20 sensors:** see [docs/ADDING_SENSORS.md](docs/ADDING_SENSORS.md)

---

## Project layout

```
TempSensor/
├── README.md
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── docker/
│   └── mqtt-publisher.Dockerfile
├── publisher/                 # Python: sensors + MQTT + CSV
│   ├── sensor/ds18b20_reader.py
│   ├── mqtt_publisher.py
│   └── mqtt_csv_logger.py
├── stack/                     # Mosquitto, Telegraf, Grafana config
│   ├── mosquitto/config/
│   ├── telegraf/
│   └── grafana/
├── scripts/
│   ├── install-docker.sh
│   ├── firstTimeSetup.sh
│   ├── activate_venv.sh
│   ├── check_pipeline.sh
│   └── grafana-entrypoint.sh
├── docs/
│   └── ADDING_SENSORS.md      # how to add more DS18B20s
└── exports/                   # CSV logs (gitignored)
```

---

## Quick start

```bash
cd ~/Projects/TempSensor
ls /sys/bus/w1/devices/28-*          # enable 1-Wire if empty
nano publisher/sensor/ds18b20_reader.py   # SENSOR_MAP — see docs/ADDING_SENSORS.md
cp .env.example .env && nano .env
docker compose up -d --build
tail -f exports/mqtt_readings.csv
```

---

## Configuration (`.env`)

| Variable | Purpose |
|----------|---------|
| `INFLUXDB_*` | InfluxDB setup + token |
| `GRAFANA_ADMIN_*` | Grafana login |
| `MQTT_TOPIC` | Default `tempsensor/readings` |
| `SAMPLE_INTERVAL` | Seconds between reads (default `1`) |
| `CSV_PATH` | Default `exports/mqtt_readings.csv` |

---

## CSV log

Every MQTT reading is appended to `exports/mqtt_readings.csv`:

`timestamp`, `sensor_id`, `sensor_label`, `temperature_c`, `temperature_f` (1 decimal)

```bash
tail -f exports/mqtt_readings.csv
mv exports/mqtt_readings.csv exports/backup.csv && docker compose restart mqtt-publisher
```

---

## Grafana dashboard

- Auto-created from `stack/grafana/dashboards/tempsensor-live.template.json`
- Edit in UI → **Save** (stored in Docker volume `grafana_data`)
- Reset to template: `docker compose down -v && docker compose up -d --build`

---

## Scripts

| Script | Use |
|--------|-----|
| `scripts/install-docker.sh` | First-time Docker on Pi (`sudo`) |
| `scripts/firstTimeSetup.sh` | Host Python venv (optional) |
| `scripts/activate_venv.sh` | Activate venv |
| `scripts/check_pipeline.sh` | Test MQTT, CSV, Influx |

Host publisher (optional):

```bash
scripts/firstTimeSetup.sh
source scripts/activate_venv.sh
MQTT_HOST=localhost python3 publisher/mqtt_publisher.py
```

---

## Verify

```bash
docker compose ps
docker compose logs mqtt-publisher --tail 5
scripts/check_pipeline.sh
```

---

## Stop

```bash
docker compose down
docker compose down -v    # wipes Influx + Grafana data (keeps host exports/)
```

---

## Do not commit

`.env`, `venv/`, `exports/*.csv`, `TempSensor Live-*.json`
