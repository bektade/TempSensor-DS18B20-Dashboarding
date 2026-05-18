# TempSensor Logger

This project reads DS18B20 temperature sensors on a Raspberry Pi and logs readings to separate CSV files for each sensor.

## Project structure

```
TempSensor/
├── README.md
├── EnvironmentSetup/     # venv setup scripts, requirements.txt
├── ETL/
│   ├── Extract/          # ds18b20_sensor_logger.py, raw sensor*.csv, archive/
│   ├── Transform/        # coalesce_sensor_data.py, coalesced_*.csv
│   └── Load/             # sensor_flask_app.py, sensorDataVisualizer.py
├── GrafanaDashboard/     # Docker: MQTT + InfluxDB + Grafana (live)
├── Doc/                  # additional notes (e.g. venv tips)
└── venv/                 # Python virtual environment (created by setup)
```

## Requirements

- Python 3
- Raspberry Pi with 1-Wire support enabled
- DS18B20 sensors connected and visible under `/sys/bus/w1/devices/`
- Python dependencies installed from `EnvironmentSetup/requirements.txt` (includes `matplotlib`)

## Setup and run

1. Open a terminal in the project folder:
   ```bash
   cd /home/raspitemp/Projects/TempSensor
   ```
2. First-time setup:
   ```bash
   ./EnvironmentSetup/firstTimeSetup.sh
   ```
3. Activate the environment:
   ```bash
   source EnvironmentSetup/activate_venv.sh
   ```
4. Run the logger (writes CSVs to `ETL/Extract/`):
   ```bash
   python3 ETL/Extract/ds18b20_sensor_logger.py
   ```

The logger prints sensor readings every 5 seconds and writes each sensor to its own timestamped CSV file in `ETL/Extract/`.

Existing CSV files for the same sensor label are moved into `ETL/Extract/archive/` when the script restarts.

## CSV format

- `timestamp`
- `sensor_id`
- `sensor_label`
- `temperature_c`
- `temperature_f`

## Add multiple sensors

Open `ETL/Extract/ds18b20_sensor_logger.py` and update `SENSOR_MAP`:

```python
SENSOR_MAP = {
    '28-0000004a6df4': 'Sensor1',
    '28-000000000000': 'Sensor2',
}
```

Output files are created per sensor, for example:

- `ETL/Extract/sensor1_4.06PM_05.17.2026.csv`
- `ETL/Extract/sensor2_4.06PM_05.17.2026.csv`

## Transform (coalesce)

Merge raw sensor files into one sorted file in `ETL/Transform/`:

```bash
python3 ETL/Transform/coalesce_sensor_data.py
```

Run coalesce automatically every 30 seconds (while the sensor logger is writing CSVs):

```bash
python3 ETL/Transform/coalesce_scheduler.py
```

Output keeps the session time and date from the source filenames, e.g. `ETL/Transform/coalesced_4.26PM_05.17.2026.csv`. Previous coalesced files are archived on each run.

## Load (visualizer)

Plot recent temperature data from `ETL/Extract/` (matplotlib):

```bash
python3 ETL/Load/sensorDataVisualizer.py
```

Different time window:

```bash
python3 ETL/Load/sensorDataVisualizer.py --minutes 60
```

Web comparison chart from the latest coalesced CSV (Flask + Plotly):

```bash
python3 ETL/Load/sensor_flask_app.py
```

Open `http://localhost:5000` in a browser. Run `coalesce_sensor_data.py` first so `ETL/Transform/` has a `coalesced_*.csv` file.

## GrafanaDashboard (live MQTT)

Docker stack for real-time charts: Mosquitto → Telegraf → InfluxDB → Grafana.

Install Docker on the Pi first if needed: `sudo GrafanaDashboard/install-docker.sh` (then log out/in).

```bash
cd GrafanaDashboard
cp .env.example .env
# Edit .env and grafana/provisioning/datasources/influxdb.yml (same InfluxDB token)
docker compose up -d
python3 GrafanaDashboard/mqtt_temperature_publisher.py
```

Open **http://localhost:3000** and the **TempSensor Live** dashboard. See [GrafanaDashboard/README.md](GrafanaDashboard/README.md) for details.

## Notes

- The script verifies that each sensor path exists before logging.
- Sensor readings are collected from all configured sensors in each loop iteration.
- Press `Ctrl+C` to stop logging.
- See `Doc/Venv Tips.md` for virtual environment commands.
