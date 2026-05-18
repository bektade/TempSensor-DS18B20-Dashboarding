FROM python:3.13-slim-bookworm

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY publisher/sensor ./sensor
COPY publisher/mqtt_publisher.py publisher/mqtt_csv_logger.py ./

ENV MQTT_HOST=mosquitto \
    MQTT_PORT=1883 \
    MQTT_TOPIC=tempsensor/readings \
    CSV_PATH=/app/exports/mqtt_readings.csv \
    SKIP_W1_MODPROBE=1

CMD ["python", "-u", "mqtt_publisher.py"]
