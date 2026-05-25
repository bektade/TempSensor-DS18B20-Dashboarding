import csv
import os
import re
import shutil
from datetime import datetime
from pathlib import Path

TIMER_START_MIN = int(os.getenv('TIMER_START_MIN', '90'))

CSV_COLUMNS = [
    'timestamp',
    'elapsed_time_in_Min',
    'Timer_in_Min',
    'sensor_id',
    'sensor_label',
    'temperature_c',
    'temperature_f',
]

def sanitize_filename_part(value: str) -> str:
    cleaned = re.sub(r'[^\w.\-]+', '_', value.strip())
    return cleaned or 'unknown'


def format_run_filename_stamp(when: datetime | None = None) -> str:
    """e.g. 2026-05-18_936PM for 18 May 2026 at 9:36 PM."""
    when = when or datetime.now()
    hour12 = when.hour % 12 or 12
    meridiem = 'AM' if when.hour < 12 else 'PM'
    date_part = when.strftime('%Y-%m-%d')
    time_part = f'{hour12}{when.minute:02d}{meridiem}'
    return f'{date_part}_{time_part}'


def format_run_csv_basename(when: datetime | None = None) -> str:
    """e.g. 2026-05-18_936PM_Pro18.1_73216-0098"""
    stamp = format_run_filename_stamp(when)
    test_unit = sanitize_filename_part(os.getenv('TEST_UNIT', ''))
    serial_number = sanitize_filename_part(os.getenv('SERIAL_NUMBER', ''))
    if not test_unit or test_unit == 'unknown' or not serial_number or serial_number == 'unknown':
        raise ValueError(
            'TEST_UNIT and SERIAL_NUMBER must be set before export. '
            'Run: cd SensorDataCollector && make startReadSensor'
        )
    return f'{stamp}_{test_unit}_{serial_number}'


EXPORT_CSV_GLOB = '*.csv'


def list_active_export_csvs(export_dir: Path) -> list[Path]:
    return sorted(
        path for path in export_dir.glob(EXPORT_CSV_GLOB)
        if path.is_file()
    )


def archive_csv_exports(export_dir: str | None = None) -> list[Path]:
    """Move active CSV files from exports/ into exports/archive/."""
    root = Path(export_dir or os.getenv('CSV_DIR', 'exports'))
    archive_dir = root / os.getenv('CSV_ARCHIVE_DIR', 'archive')
    archive_dir.mkdir(parents=True, exist_ok=True)
    archived: list[Path] = []
    for path in list_active_export_csvs(root):
        if not path.is_file():
            continue
        dest = archive_dir / path.name
        if dest.exists():
            suffix = datetime.now().strftime('%Y%m%d_%H%M%S')
            dest = archive_dir / f'{path.stem}_{suffix}{path.suffix}'
        shutil.move(str(path), str(dest))
        archived.append(dest)
    return archived


def new_run_csv_path(export_dir: str | None = None) -> Path:
    """Create a new CSV path: date_time_TestUnit_serialNumber.csv"""
    directory = Path(export_dir or os.getenv('CSV_DIR', 'exports'))
    directory.mkdir(parents=True, exist_ok=True)
    return directory / f'{format_run_csv_basename()}.csv'


def session_start_timestamp(csv_path: Path, reading_timestamp: int) -> int:
    if not csv_path.exists() or csv_path.stat().st_size == 0:
        return reading_timestamp
    with csv_path.open(newline='') as handle:
        first_row = next(csv.DictReader(handle), None)
    if first_row is None:
        return reading_timestamp
    return int(datetime.strptime(first_row['timestamp'], '%Y-%m-%d %H:%M:%S').timestamp())


def elapsed_minutes_value(reading_timestamp: int, session_start: int) -> int:
    return max(0, (reading_timestamp - session_start) // 60)


def timer_in_min_value(elapsed_minutes: int) -> int:
    return max(0, TIMER_START_MIN - elapsed_minutes)


def append_mqtt_reading_csv(payload: dict, csv_path: str | Path) -> None:
    path = Path(csv_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    reading_timestamp = int(payload['timestamp'])
    session_start = session_start_timestamp(path, reading_timestamp)
    elapsed = elapsed_minutes_value(reading_timestamp, session_start)
    row = {
        'timestamp': datetime.fromtimestamp(reading_timestamp).isoformat(sep=' '),
        'elapsed_time_in_Min': elapsed,
        'Timer_in_Min': timer_in_min_value(elapsed),
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
