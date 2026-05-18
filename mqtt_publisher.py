import argparse
import json
import os
import time

import paho.mqtt.client as mqtt

from sensor.ds18b20_reader import SAMPLE_INTERVAL, load_sensors


def publish_readings(client: mqtt.Client, sensors, topic: str) -> None:
    for sensor in sensors:
        payload = sensor.build_payload()
        client.publish(topic, json.dumps(payload), qos=0)
        print(
            f'[{payload["timestamp"]}] MQTT {sensor.label}: '
            f'C={payload["temperature_c"]} F={payload["temperature_f"]}'
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Read DS18B20 sensors and publish readings to MQTT for Grafana.'
    )
    parser.add_argument('--host', default=os.getenv('MQTT_HOST', 'localhost'))
    parser.add_argument('--port', type=int, default=int(os.getenv('MQTT_PORT', '1883')))
    parser.add_argument('--topic', default=os.getenv('MQTT_TOPIC', 'tempsensor/readings'))
    parser.add_argument('--interval', type=int, default=int(os.getenv('SAMPLE_INTERVAL', SAMPLE_INTERVAL)))
    args = parser.parse_args()

    sensors = load_sensors()
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
