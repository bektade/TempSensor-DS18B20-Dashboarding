#!/bin/sh
set -eu

mkdir -p /etc/grafana/provisioning/datasources
mkdir -p /etc/grafana/provisioning/dashboards/json

sed \
  -e "s|INFLUXDB_ADMIN_TOKEN_PLACEHOLDER|${INFLUXDB_ADMIN_TOKEN}|g" \
  -e "s|INFLUXDB_ORG_PLACEHOLDER|${INFLUXDB_ORG}|g" \
  -e "s|INFLUXDB_BUCKET_PLACEHOLDER|${INFLUXDB_BUCKET}|g" \
  /etc/grafana/provisioning/datasources/influxdb.yml.template \
  > /etc/grafana/provisioning/datasources/influxdb.yml

sed 's/"id": [0-9]*,//' \
  /etc/grafana/provisioning/dashboards/tempsensor-live.template.json \
  > /etc/grafana/provisioning/dashboards/json/tempsensor-live.json

exec /run.sh
