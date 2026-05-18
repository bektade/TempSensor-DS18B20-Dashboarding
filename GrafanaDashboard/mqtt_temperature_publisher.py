import argparse
import json
import os
import sys
import time
from datetime import datetime

import paho.mqtt.client as mqtt

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXTRACT_DIR = os.path.join(PROJECT_ROOT, 'ETL', 'Extract')
sys.path.insert(0, EXTRACT_DIR)

from ds18b20_sensor_logger import SAMPLE_INTERVAL, SENSOR_MAP, load_sensors  # noqa: E402


def build_payload(sensor, timestamp):
    temp_c, temp_f = sensor.read_temp()
    return {
        'timestamp': timestamp,
        'sensor_id': sensor.sensor_id,
        'sensor_label': sensor.label,
        'temperature_c': round(temp_c, 3),
        'temperature_f': round(temp_f, 3),
    }


def publish_readings(client, sensors, topic):
    timestamp = datetime.now().isoformat(sep=' ')
    for sensor in sensors:
        payload = build_payload(sensor, timestamp)
        client.publish(topic, json.dumps(payload), qos=0)
        print(
            f'[{timestamp}] MQTT {sensor.label}: '
            f'C={payload["temperature_c"]} F={payload["temperature_f"]}'
        )


def main():
    parser = argparse.ArgumentParser(
        description='Publish DS18B20 readings to MQTT for Grafana/InfluxDB.'
    )
    parser.add_argument('--host', default=os.getenv('MQTT_HOST', 'localhost'))
    parser.add_argument('--port', type=int, default=int(os.getenv('MQTT_PORT', '1883')))
    parser.add_argument('--topic', default=os.getenv('MQTT_TOPIC', 'tempsensor/readings'))
    parser.add_argument('--interval', type=int, default=SAMPLE_INTERVAL)
    args = parser.parse_args()

    sensors = load_sensors(SENSOR_MAP)
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.connect(args.host, args.port, keepalive=60)
    client.loop_start()

    print(f'Publishing to mqtt://{args.host}:{args.port}/{args.topic} every {args.interval}s')

    try:
        while True:
            publish_readings(client, sensors, args.topic)
            if len(sensors) > 1:
                print('---')
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print('\nMQTT publisher stopped.')
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == '__main__':
    main()
