import csv
import os
import shutil
from datetime import datetime
from pathlib import Path

CSV_COLUMNS = [
    'timestamp',
    'sensor_id',
    'sensor_label',
    'temperature_c',
    'temperature_f',
]

def format_run_filename_stamp(when: datetime | None = None) -> str:
    """e.g. 2026-05-18_936PM for 18 May 2026 at 9:36 PM."""
    when = when or datetime.now()
    hour12 = when.hour % 12 or 12
    meridiem = 'AM' if when.hour < 12 else 'PM'
    date_part = when.strftime('%Y-%m-%d')
    time_part = f'{hour12}{when.minute:02d}{meridiem}'
    return f'{date_part}_{time_part}'


RUN_CSV_GLOB = 'temp_reading_*.csv'


def archive_csv_exports(export_dir: str | None = None) -> list[Path]:
    """Move active CSV files from exports/ into exports/archive/."""
    root = Path(export_dir or os.getenv('CSV_DIR', 'exports'))
    archive_dir = root / os.getenv('CSV_ARCHIVE_DIR', 'archive')
    archive_dir.mkdir(parents=True, exist_ok=True)
    archived: list[Path] = []
    for path in sorted(root.glob(RUN_CSV_GLOB)):
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
    """Create a new CSV path for this publisher run (date + 12h time in filename)."""
    directory = Path(export_dir or os.getenv('CSV_DIR', 'exports'))
    directory.mkdir(parents=True, exist_ok=True)
    return directory / f'temp_reading_{format_run_filename_stamp()}.csv'


def append_mqtt_reading_csv(payload: dict, csv_path: str | Path) -> None:
    path = Path(csv_path)
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
