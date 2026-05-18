import os
import time
from datetime import datetime

BASE_DIR = '/sys/bus/w1/devices/'
SAMPLE_INTERVAL = 30

SENSOR_MAP = {
    '28-0000004a6df4': 'Sensor1',
    # '28-000000000000': 'Sensor2',
}

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')


class DS18B20Sensor:
    def __init__(self, sensor_id: str, label: str, base_dir: str = BASE_DIR) -> None:
        self.sensor_id = sensor_id
        self.label = label
        self.base_dir = base_dir
        self.device_path = os.path.join(self.base_dir, self.sensor_id)
        if not os.path.exists(self.device_path):
            raise FileNotFoundError(f'Device path not found: {self.device_path}')

    def read_temp_raw(self) -> tuple[str, str]:
        with open(os.path.join(self.device_path, 'w1_slave'), 'r') as f:
            valid, temp = f.readlines()
        return valid, temp

    def read_temp(self) -> tuple[float, float]:
        valid, temp = self.read_temp_raw()
        while 'YES' not in valid:
            time.sleep(0.2)
            valid, temp = self.read_temp_raw()

        pos = temp.index('t=')
        if pos == -1:
            raise RuntimeError('Failed to parse temperature from sensor output')

        temp_c = float(temp[pos + 2:]) / 1000.0
        temp_f = temp_c * (9.0 / 5.0) + 32.0
        return temp_c, temp_f

    def build_payload(self, timestamp: str | None = None) -> dict[str, str | float]:
        temp_c, temp_f = self.read_temp()
        if timestamp is None:
            timestamp = datetime.now().isoformat(sep=' ')
        return {
            'timestamp': timestamp,
            'sensor_id': self.sensor_id,
            'sensor_label': self.label,
            'temperature_c': round(temp_c, 3),
            'temperature_f': round(temp_f, 3),
        }


def load_sensors(sensor_map: dict[str, str] | None = None) -> list[DS18B20Sensor]:
    mapping = sensor_map if sensor_map is not None else SENSOR_MAP
    return [DS18B20Sensor(sensor_id, label) for sensor_id, label in mapping.items()]


def main() -> None:
    sensors = load_sensors()
    try:
        while True:
            timestamp = datetime.now().isoformat(sep=' ')
            for sensor in sensors:
                payload = sensor.build_payload(timestamp)
                print(
                    f'[{payload["timestamp"]}] {sensor.label}: '
                    f'C={payload["temperature_c"]} F={payload["temperature_f"]}'
                )
            if len(sensors) > 1:
                print('---')
            time.sleep(SAMPLE_INTERVAL)
    except KeyboardInterrupt:
        print('\nSensor read loop stopped.')


if __name__ == '__main__':
    main()
