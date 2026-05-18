# Adding more DS18B20 sensors

This guide is for the **Grafana** branch on a **Raspberry Pi**. Each sensor gets its own 1-Wire ID, a label in software, and appears separately in MQTT, CSV, InfluxDB, and Grafana.

---

## What you need

- DS18B20 sensors (each has a unique factory ID)
- 1-Wire wiring: data, ground, and 3.3 V (or 5 V per your board)
- 4.7 kΩ pull-up resistor on the data line (one resistor for the bus is enough for short runs)
- 1-Wire enabled on the Pi

---

## 1. Enable 1-Wire on the Pi

```bash
sudo raspi-config
```

**Interface Options → 1-Wire → Enable**, then reboot:

```bash
sudo reboot
```

After reboot, the kernel should load the bus:

```bash
ls /sys/bus/w1/devices/
```

You should see folders starting with `28-` (temperature sensors) and possibly `00-` (bus master).

---

## 2. Find each sensor’s ID

With **only one sensor** connected, note its folder name:

```bash
ls /sys/bus/w1/devices/28-*
```

Example: `28-0000004a6df4`

Connect the **next** sensor (power off if you prefer), wait a few seconds, then list again:

```bash
ls /sys/bus/w1/devices/28-*
```

You should see **two** folders, for example:

```
28-0000004a6df4
28-031731d057ff
```

The folder name (without path) is the **sensor_id** you put in `SENSOR_MAP`.

### Quick read test

```bash
cat /sys/bus/w1/devices/28-0000004a6df4/w1_slave
```

Look for `YES` on the first line and `t=...` on the second (millidegrees Celsius).

---

## 3. Edit `SENSOR_MAP`

Open:

`publisher/sensor/ds18b20_reader.py`

Add one line per sensor: **ID → label** (label is any short name you choose; it appears in Grafana and CSV).

```python
SENSOR_MAP = {
    '28-0000004a6df4': 'Sensor1',
    '28-031731d057ff': 'Sauna',
    '28-000000000000': 'Outdoor',   # example — use your real ID
}
```

| Key | Value |
|-----|--------|
| **Key** (`28-...`) | Exact folder name under `/sys/bus/w1/devices/` |
| **Value** | Human-readable name (letters/numbers; avoid spaces if possible) |

Labels must be **unique**. They are stored as `sensor_label` in MQTT, CSV, and InfluxDB.

---

## 4. Apply the change

Rebuild and restart the publisher (Docker):

```bash
cd ~/Projects/TempSensor
docker compose build mqtt-publisher
docker compose up -d mqtt-publisher
```

Check logs — each sensor should print every second:

```bash
docker compose logs mqtt-publisher --tail 20
```

Example:

```
MQTT Sensor1: C=26.1 F=78.9 -> CSV
MQTT Sauna: C=85.3 F=185.5 -> CSV
---
```

---

## 5. Verify data paths

### MQTT

```bash
mosquitto_sub -h localhost -t 'tempsensor/readings' -v
```

You should see one JSON message **per sensor** per cycle, each with its own `sensor_id` and `sensor_label`.

### CSV

```bash
tail -f exports/mqtt_readings.csv
```

Multiple rows per timestamp (one per sensor) is normal.

### Grafana

1. Open **TempSensor Live**.
2. **Sensor** dropdown → refresh or pick **All** — new labels should appear after data arrives.
3. If a sensor is missing, set time range to **Last 15 minutes** and wait for new points.

No dashboard code changes are required; the template already filters by `sensor_label`.

---

## 6. Optional: test without Docker

```bash
cd ~/Projects/TempSensor
source scripts/activate_venv.sh
python3 publisher/sensor/ds18b20_reader.py
```

Reads all sensors in `SENSOR_MAP` once per second and prints to the terminal (no MQTT).

---

## Wiring notes (multiple sensors)

- All DS18B20 **data** pins can share one **data** GPIO line (parallel 1-Wire bus).
- Share **ground** and use appropriate **VDD** per sensor datasheet.
- Keep cable runs reasonable; long or noisy runs may need stronger pull-up or parasitic power planning.

```
        3.3V (or 5V)
           |
    [4.7kΩ pull-up to DATA]
           |
    GPIO --+-- DATA  Sensor1
           +-- DATA  Sensor2
           +-- DATA  Sensor3
    GND  ---+-- GND   (all sensors)
```

---

## Troubleshooting

| Problem | What to try |
|---------|-------------|
| New sensor not in `ls /sys/bus/w1/devices/28-*` | Check wiring, power, reboot, re-enable 1-Wire in `raspi-config` |
| `Device path not found` in publisher logs | Wrong ID in `SENSOR_MAP` — copy folder name exactly |
| Only one sensor reads | Duplicate ID in map, bad wiring, or weak pull-up |
| Grafana shows old sensors only | Set **Sensor → All**, widen time range, confirm new MQTT messages |
| Publisher exits on start | One ID in `SENSOR_MAP` has no device folder — fix map or connect sensor |

### Publisher fails inside Docker but works on host

The container mounts `/sys/bus/w1/devices` from the Pi. If the host sees sensors but the container does not:

```bash
ls /sys/bus/w1/devices/28-*
docker compose exec mqtt-publisher ls /sys/bus/w1/devices/28-*
```

Both lists should match. If the container list is empty, restart Docker or the Pi after enabling 1-Wire.

---

## Summary checklist

1. [ ] 1-Wire enabled, Pi rebooted  
2. [ ] Each sensor appears as `28-xxxxxxxxxxxx` under `/sys/bus/w1/devices/`  
3. [ ] `SENSOR_MAP` updated in `publisher/sensor/ds18b20_reader.py`  
4. [ ] `docker compose build mqtt-publisher && docker compose up -d mqtt-publisher`  
5. [ ] Logs, MQTT, CSV, and Grafana show all labels  
