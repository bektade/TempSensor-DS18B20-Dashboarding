# InfluxDB

InfluxDB stores live temperature readings for **Grafana**. Data flows:

```
mqtt-publisher → MQTT → Telegraf → InfluxDB → Grafana
```

CSV files in `exports/` are separate; cleaning InfluxDB does not delete CSVs.

---

## Configuration (`.env`)

Copy from `.env.example` and set before first `docker compose up -d`:

| Variable | Default | Purpose |
|----------|---------|---------|
| `INFLUXDB_USERNAME` | `admin` | Admin user (first boot only) |
| `INFLUXDB_PASSWORD` | *(change me)* | Admin password |
| `INFLUXDB_ORG` | `tempsensor` | Organization name |
| `INFLUXDB_BUCKET` | `temperature` | Bucket for all sensor points |
| `INFLUXDB_ADMIN_TOKEN` | *(change me)* | API token for Telegraf + Grafana |

Telegraf and Grafana read these values from `.env` at container start.

---

## Service

| Item | Value |
|------|--------|
| Container | `tempsensor-influxdb` |
| Image | `influxdb:2.7` |
| Host URL | http://localhost:8086 |
| Docker URL | http://influxdb:8086 |

Start with the full stack:

```bash
cd ~/Projects/TempSensor/SensorDataCollector
docker compose up -d
```

Check status:

```bash
docker compose ps influxdb
docker compose logs influxdb --tail 30
```

---

## Data model

Telegraf writes MQTT JSON into InfluxDB (`stack/telegraf/telegraf.conf.template`):

| Item | Value |
|------|--------|
| Measurement | `sensor_reading` |
| Tags | `sensor_id`, `sensor_label` |
| Fields | `temperature_c`, `temperature_f` |
| Timestamp | Unix time from MQTT payload |

Example Flux query (last 10 minutes, point count):

```bash
docker compose exec influxdb influx query \
  --org tempsensor \
  --token "$INFLUXDB_ADMIN_TOKEN" \
  'from(bucket: "temperature")
    |> range(start: -10m)
    |> filter(fn: (r) => r._measurement == "sensor_reading")
    |> count()'
```

Use your real org, bucket, and token from `.env`.

---

## Verify the pipeline

```bash
./scripts/check_pipeline.sh
```

Shows container status, Telegraf logs, MQTT sample, CSV tail, and InfluxDB point count.

---

## Clean database (keep CSV)

Wipe InfluxDB so Grafana starts fresh **without** deleting CSV files:

```bash
./scripts/clean_influx_data.sh
```

Confirm with `y`, or skip the prompt:

```bash
./scripts/clean_influx_data.sh -y
```

Delete only the `sensor_reading` measurement (bucket otherwise unchanged):

```bash
./scripts/clean_influx_data.sh -y --measurement sensor_reading
```

The stack keeps running; new readings continue into Influx and the current CSV.

---

## Reset InfluxDB completely

Removes all Influx data and re-runs first-time setup from `.env` (also affects Grafana’s data source if the token changes):

```bash
docker compose down
docker volume rm tempsensor_influxdb_data
docker compose up -d
```

Then open Grafana and confirm **Dashboards → TempSensor → TempSensor Live** still loads.

---

## Grafana connection

Grafana uses a provisioned InfluxDB datasource (`stack/grafana/templates/influxdb.yml.template`) with the same org, bucket, and token as `.env`.

If Grafana shows “no data” but MQTT/CSV work:

1. Run `./scripts/check_pipeline.sh`
2. Confirm `docker compose ps` shows `influxdb` and `telegraf` healthy
3. Confirm `INFLUXDB_*` in `.env` matches what Influx was initialized with (or reset volume above)

Dashboard details: see the **Grafana dashboard** section in [README.md](../README.md).
