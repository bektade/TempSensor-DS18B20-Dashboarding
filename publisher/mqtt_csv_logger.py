import csv
import os
from datetime import datetime
from pathlib import Path

CSV_COLUMNS = [
    'timestamp',
    'sensor_id',
    'sensor_label',
    'temperature_c',
    'temperature_f',
]


def append_mqtt_reading_csv(payload: dict, csv_path: str | None = None) -> None:
    path = Path(csv_path or os.getenv('CSV_PATH', 'exports/mqtt_readings.csv'))
    path.parent.mkdir(parents=True, exist_ok=True)
    row = {
        'timestamp': datetime.fromtimestamp(int(payload['timestamp'])).isoformat(sep=' '),
        'sensor_id': payload['sensor_id'],
        'sensor_label': payload['sensor_label'],
        'temperature_c': payload['temperature_c'],
        'temperature_f': payload['temperature_f'],
    }
    write_header = not path.exists() or path.stat().st_size == 0
    with path.open('a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=CSV_COLUMNS)
        if write_header:
            writer.writeheader()
        writer.writerow(row)
