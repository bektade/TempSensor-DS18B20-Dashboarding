import csv
import glob
import json
import os
import re
import sys
from datetime import datetime

from flask import Flask, render_template

LOAD_DIR = os.path.dirname(os.path.abspath(__file__))
ETL_DIR = os.path.dirname(LOAD_DIR)
TRANSFORM_DIR = os.path.join(ETL_DIR, 'Transform')
INFO_FILE = os.path.join(LOAD_DIR, 'info.text')

sys.path.insert(0, TRANSFORM_DIR)

app = Flask(__name__, template_folder=os.path.join(LOAD_DIR, 'templates'))


def find_latest_coalesced_csv(transform_dir=TRANSFORM_DIR):
    pattern = os.path.join(transform_dir, 'coalesced_*.csv')
    files = glob.glob(pattern)
    if not files:
        return None
    return max(files, key=os.path.getmtime)


def load_coalesced_rows(csv_path):
    with open(csv_path, 'r', newline='') as handle:
        return list(csv.DictReader(handle))


def parse_sauna_value(value):
    if not value:
        return None, None
    match = re.match(r'^(.+?)\s*\(\s*([^)]+)\s*\)\s*$', value)
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return value.strip(), None


def load_test_info(info_path=INFO_FILE):
    info = {'sauna_name': None, 'sauna_serial': None, 'test_date': None}
    if not os.path.isfile(info_path):
        return info

    with open(info_path, 'r', encoding='utf-8') as handle:
        for line in handle:
            line = line.strip()
            if not line or ':' not in line:
                continue
            key, _, value = line.partition(':')
            key = key.strip().lower()
            value = value.strip()
            if key == 'sauna':
                model, serial = parse_sauna_value(value)
                info['sauna_name'] = model
                info['sauna_serial'] = serial
            elif key in ('s/n', 'serial', 'serial number'):
                info['sauna_serial'] = value
            elif key == 'test date':
                info['test_date'] = value
    return info


def format_chart_title(info):
    sauna_name = info.get('sauna_name')
    sauna_serial = info.get('sauna_serial')
    test_date = info.get('test_date')

    parts = []
    if sauna_name or sauna_serial:
        serial_label = sauna_serial if sauna_serial else '....'
        name_label = sauna_name if sauna_name else ''
        parts.append(f'Sauna : {name_label} ( S/N : {serial_label})')
    if test_date:
        parts.append(f'Test Date : {test_date}')

    if not parts:
        return 'Sensor temperature comparison'
    return ' | '.join(parts)


def group_sensor_readings(rows):
    grouped = {}
    for row in rows:
        label = row.get('sensor_label') or row.get('sensor_id')
        if not label:
            continue
        try:
            timestamp = datetime.fromisoformat(row['timestamp'])
            temp_c = float(row['temperature_c'])
            temp_f = float(row['temperature_f'])
        except (TypeError, ValueError):
            continue
        grouped.setdefault(label, []).append({
            'timestamp': timestamp.isoformat(sep=' '),
            'temp_c': temp_c,
            'temp_f': temp_f,
        })

    for label in grouped:
        grouped[label].sort(key=lambda point: point['timestamp'])
    return grouped


def render_index(**context):
    chart_title = format_chart_title(load_test_info())
    return render_template(
        'index.html',
        chart_title=chart_title,
        **context,
    )


@app.route('/')
def index():
    csv_path = find_latest_coalesced_csv()
    if csv_path is None:
        return render_index(
            error='No coalesced CSV found in ETL/Transform. Run coalesce_sensor_data.py first.',
            readings_json=None,
            source_file=None,
            sensor_labels=[],
        )

    rows = load_coalesced_rows(csv_path)
    grouped = group_sensor_readings(rows)
    if not grouped:
        return render_index(
            error='Coalesced file has no readable sensor rows.',
            readings_json=None,
            source_file=os.path.basename(csv_path),
            sensor_labels=[],
        )

    sensor_labels = sorted(grouped)
    return render_index(
        error=None,
        readings_json=json.dumps(grouped),
        source_file=os.path.basename(csv_path),
        sensor_labels=sensor_labels,
    )


def main():
    app.run(host='0.0.0.0', port=5000, debug=True)


if __name__ == '__main__':
    main()
