import argparse
import csv
import glob
import os
from datetime import datetime

FIELDNAMES = ('timestamp', 'sensor_id', 'sensor_label', 'temperature_c', 'temperature_f')
TRANSFORM_DIR = os.path.dirname(os.path.abspath(__file__))
ARCHIVE_DIR = 'archive'
ETL_DIR = os.path.dirname(TRANSFORM_DIR)
PROJECT_ROOT = os.path.dirname(ETL_DIR)
EXTRACT_DIR = os.path.join(ETL_DIR, 'Extract')
DEFAULT_CSV_DIR = EXTRACT_DIR


def session_suffix_from_csv_path(csv_path):
    stem = os.path.splitext(os.path.basename(csv_path))[0]
    parts = stem.split('_', 1)
    if len(parts) == 2 and parts[0].lower().startswith('sensor'):
        return parts[1]
    return None


def build_coalesced_output_path(csv_paths, transform_dir=TRANSFORM_DIR):
    suffixes = {session_suffix_from_csv_path(path) for path in csv_paths}
    suffixes.discard(None)
    if len(suffixes) == 1:
        filename = f'coalesced_{next(iter(suffixes))}.csv'
    else:
        filename = 'coalesced_sensors.csv'
    return os.path.join(transform_dir, filename)


def sensor_label_from_csv_path(csv_path):
    stem = os.path.splitext(os.path.basename(csv_path))[0]
    prefix = stem.split('_', 1)[0].lower()
    if prefix.startswith('sensor') and prefix[6:].isdigit():
        return f'Sensor{prefix[6:]}'
    return None


def coalesce_sensor_csvs(csv_paths):
    rows = []
    for path in csv_paths:
        file_label = sensor_label_from_csv_path(path)
        with open(path, 'r', newline='') as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if not row.get('timestamp'):
                    continue
                if file_label:
                    row = dict(row)
                    row['sensor_label'] = file_label
                rows.append(row)
    rows.sort(key=lambda row: (row['timestamp'], row.get('sensor_label', '')))
    return rows


def write_coalesced_csv(rows, output_path):
    with open(output_path, 'w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def archive_existing_coalesced(transform_dir=TRANSFORM_DIR):
    archive_dir = os.path.join(transform_dir, ARCHIVE_DIR)
    os.makedirs(archive_dir, exist_ok=True)

    archived = []
    for path in sorted(glob.glob(os.path.join(transform_dir, 'coalesced_*.csv'))):
        filename = os.path.basename(path)
        archive_path = os.path.join(archive_dir, filename)
        if os.path.exists(archive_path):
            stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            archive_path = os.path.join(archive_dir, f'{stamp}_{filename}')
        os.rename(path, archive_path)
        archived.append(filename)
    return archived


def find_sensor_csv_files(csv_dir=DEFAULT_CSV_DIR):
    pattern = os.path.join(csv_dir, 'sensor*.csv')
    return sorted(
        path for path in glob.glob(pattern)
        if not os.path.basename(path).startswith('coalesced_')
    )


def group_rows_by_sensor(rows):
    grouped = {}
    for row in rows:
        label = row.get('sensor_label') or row.get('sensor_id')
        if not label:
            continue
        try:
            timestamp = datetime.fromisoformat(row['timestamp'])
            temp_c = float(row['temperature_c'])
        except (TypeError, ValueError):
            continue
        grouped.setdefault(label, []).append((timestamp, temp_c))

    for label in grouped:
        grouped[label].sort(key=lambda point: point[0])
    return grouped


def main():
    parser = argparse.ArgumentParser(
        description='Merge rows from multiple sensor CSV files into one sorted file.'
    )
    parser.add_argument(
        'csv_files',
        nargs='*',
        help='Sensor CSV files to merge (default: sensor*.csv in ETL/Extract)',
    )
    parser.add_argument(
        '--csv-dir',
        default=DEFAULT_CSV_DIR,
        help='Directory to search for sensor CSV files (default: ETL/Extract)',
    )
    parser.add_argument(
        '-o',
        '--output',
        default=None,
        help='Output CSV path (default: ETL/Transform/coalesced_<time>_<date>.csv)',
    )
    args = parser.parse_args()

    csv_files = args.csv_files or find_sensor_csv_files(args.csv_dir)
    if not csv_files:
        raise SystemExit(f'No sensor CSV files found in {os.path.abspath(args.csv_dir)}')

    rows = coalesce_sensor_csvs(csv_files)
    if not rows:
        raise SystemExit('No rows found in the given CSV files.')

    output_path = args.output or build_coalesced_output_path(csv_files)
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    archived = archive_existing_coalesced(os.path.dirname(os.path.abspath(output_path)))
    for filename in archived:
        print(f'Archived {filename}')

    write_coalesced_csv(rows, output_path)
    sensors = sorted(group_rows_by_sensor(rows))
    print(f'Wrote {len(rows)} rows from {len(csv_files)} file(s) to {output_path} ({len(sensors)} sensor(s): {", ".join(sensors)})')


if __name__ == '__main__':
    main()
