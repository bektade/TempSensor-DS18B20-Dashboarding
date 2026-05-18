import csv
import glob
import os
import time
from datetime import datetime

BASE_DIR = '/sys/bus/w1/devices/'
EXTRACT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_DIR = EXTRACT_DIR
ARCHIVE_DIR = 'archive'
SAMPLE_INTERVAL = 30

SENSOR_MAP = {
    '28-0000004a6df4': 'Sensor1',
    # Add more sensors here:
    # '28-000000000000': 'Sensor2',
}

# these two lines mount the device:
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')


class DS18B20Sensor:
    def __init__(self, sensor_id, label, csv_dir=CSV_DIR, base_dir=BASE_DIR, sample_interval=SAMPLE_INTERVAL):
        self.sensor_id = sensor_id
        self.label = label
        self.base_dir = base_dir
        self.sample_interval = sample_interval
        self.device_path = os.path.join(self.base_dir, self.sensor_id)
        self.created_at = datetime.now()
        self.safe_label = self._safe_label(self.label)
        self.csv_file = self._build_csv_path(csv_dir)
        self.archive_dir = os.path.join(csv_dir, ARCHIVE_DIR)

        if not os.path.exists(self.device_path):
            raise FileNotFoundError(f'Device path not found: {self.device_path}')

        self._prepare_dirs(csv_dir, self.archive_dir)
        self._archive_existing_files(csv_dir)
        self.ensure_csv_header(self.csv_file)

    def _build_csv_path(self, csv_dir):
        time_label = self.created_at.strftime('%I.%M%p').lstrip('0')
        date_label = self.created_at.strftime('%m.%d.%Y')
        filename = f'{self.safe_label.lower()}_{time_label}_{date_label}.csv'
        return os.path.join(csv_dir, filename)

    @staticmethod
    def _safe_label(label):
        return ''.join(
            c if c.isalnum() or c in ('-', '_') else '_'
            for c in label
        )

    @staticmethod
    def _prepare_dirs(csv_dir, archive_dir):
        os.makedirs(csv_dir, exist_ok=True)
        os.makedirs(archive_dir, exist_ok=True)

    def _archive_existing_files(self, csv_dir):
        pattern = os.path.join(csv_dir, f'{self.safe_label.lower()}_*.csv')
        for path in glob.glob(pattern):
            if os.path.abspath(path) == os.path.abspath(self.csv_file):
                continue
            if os.path.dirname(os.path.abspath(path)) == os.path.abspath(self.archive_dir):
                continue

            archive_path = os.path.join(self.archive_dir, os.path.basename(path))
            if os.path.exists(archive_path):
                archive_suffix = datetime.now().strftime('%Y%m%d_%H%M%S')
                archive_path = os.path.join(
                    self.archive_dir,
                    f'{archive_suffix}_{os.path.basename(path)}'
                )
            os.rename(path, archive_path)

    def read_temp_raw(self):
        with open(os.path.join(self.device_path, 'w1_slave'), 'r') as f:
            valid, temp = f.readlines()
        return valid, temp

    def read_temp(self):
        valid, temp = self.read_temp_raw()

        while 'YES' not in valid:
            time.sleep(0.2)
            valid, temp = self.read_temp_raw()

        pos = temp.index('t=')
        if pos == -1:
            raise RuntimeError('Failed to parse temperature from sensor output')

        temp_string = temp[pos + 2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * (9.0 / 5.0) + 32.0
        return temp_c, temp_f

    @staticmethod
    def ensure_csv_header(path):
        if not os.path.exists(path):
            with open(path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['timestamp', 'sensor_id', 'sensor_label', 'temperature_c', 'temperature_f'])

    def append_csv(self, timestamp, temp_c, temp_f):
        with open(self.csv_file, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                timestamp,
                self.sensor_id,
                self.label,
                '{:.3f}'.format(temp_c),
                '{:.3f}'.format(temp_f),
            ])

    def log_reading(self):
        temp_c, temp_f = self.read_temp()
        timestamp = datetime.now().isoformat(sep=' ')
        self.append_csv(timestamp, temp_c, temp_f)
        print(f'[{timestamp}] {self.label}: C={temp_c:,.3f} F={temp_f:,.3f}')


def load_sensors(sensor_map):
    sensors = []
    for sensor_id, label in sensor_map.items():
        sensors.append(DS18B20Sensor(sensor_id, label))
    return sensors


def main():
    sensors = load_sensors(SENSOR_MAP)

    try:
        while True:
            for sensor in sensors:
                sensor.log_reading()
            if len(sensors) > 1:
                print('---')
            time.sleep(SAMPLE_INTERVAL)
    except KeyboardInterrupt:
        print('\nLogging stopped by user.')


if __name__ == '__main__':
    main()