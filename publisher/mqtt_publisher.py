import argparse
import json
import os
import sys
import time
from pathlib import Path

_PUBLISHER_DIR = Path(__file__).resolve().parent
if str(_PUBLISHER_DIR) not in sys.path:
    sys.path.insert(0, str(_PUBLISHER_DIR))

import paho.mqtt.client as mqtt

from mqtt_csv_logger import append_mqtt_reading_csv
from sensor.ds18b20_reader import SAMPLE_INTERVAL, load_sensors


def publish_readings(client: mqtt.Client, sensors, topic: str, csv_path: str) -> None:
    for sensor in sensors:
        payload = sensor.build_payload()
        client.publish(topic, json.dumps(payload), qos=0)
        append_mqtt_reading_csv(payload, csv_path)
        print(
            f'[{payload["timestamp"]}] MQTT {sensor.label}: '
            f'C={payload["temperature_c"]:.1f} F={payload["temperature_f"]:.1f} '
            f'-> CSV'
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Read DS18B20 sensors, publish to MQTT, and append each reading to CSV.'
    )
    parser.add_argument('--host', default=os.getenv('MQTT_HOST', 'localhost'))
    parser.add_argument('--port', type=int, default=int(os.getenv('MQTT_PORT', '1883')))
    parser.add_argument('--topic', default=os.getenv('MQTT_TOPIC', 'tempsensor/readings'))
    parser.add_argument('--interval', type=int, default=int(os.getenv('SAMPLE_INTERVAL', SAMPLE_INTERVAL)))
    parser.add_argument('--csv', default=os.getenv('CSV_PATH', 'exports/mqtt_readings.csv'))
    args = parser.parse_args()

    sensors = load_sensors()
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.connect(args.host, args.port, keepalive=60)
    client.loop_start()

    print(f'Publishing to mqtt://{args.host}:{args.port}/{args.topic} every {args.interval}s')
    print(f'CSV log: {args.csv}')

    try:
        while True:
            publish_readings(client, sensors, args.topic, args.csv)
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
