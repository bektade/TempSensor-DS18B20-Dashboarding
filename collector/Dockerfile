# MQTT / Grafana sensor data collector
# Build context: repo root (TempSensor/)
# Reads DS18B20 via 1-Wire, publishes JSON to MQTT, logs CSV exports.

FROM python:3.13-slim-bookworm

LABEL org.opencontainers.image.title="tempsensor-mqtt-collector" \
      org.opencontainers.image.description="DS18B20 sensor reader — MQTT publish + CSV export for Grafana stack"

WORKDIR /app

COPY requirements.txt .
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        tzdata \
        libglib2.0-0 \
        libnss3 \
        libatk1.0-0 \
        libatk-bridge2.0-0 \
        libcups2 \
        libdrm2 \
        libxkbcommon0 \
        libgbm1 \
        libxcomposite1 \
        libxdamage1 \
        libxfixes3 \
        libxrandr2 \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir -r requirements.txt

COPY publisher/sensor ./sensor
COPY publisher/mqtt_publisher.py publisher/mqtt_csv_logger.py ./
COPY Visualize/sensorDataVisualizer.py ./Visualize/
COPY collector/entrypoint.sh /mqtt-publisher-entrypoint.sh
RUN chmod +x /mqtt-publisher-entrypoint.sh

ENV TZ=America/Chicago \
    MQTT_HOST=mosquitto \
    MQTT_PORT=1883 \
    MQTT_TOPIC=tempsensor/readings \
    CSV_DIR=/app/exports \
    VISUALIZE_OUTPUT_DIR=/app/Visualize/output \
    MPLCONFIGDIR=/tmp/matplotlib \
    SKIP_W1_MODPROBE=1

ENTRYPOINT ["/mqtt-publisher-entrypoint.sh"]
