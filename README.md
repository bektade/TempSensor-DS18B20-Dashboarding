# TempSensor

Two independent stacks in one repo:

| Part | Purpose | Start |
|------|---------|--------|
| **[SensorDataCollector](SensorDataCollector/)** | DS18B20 → MQTT → InfluxDB → Grafana + CSV export | `cd SensorDataCollector && make startReadSensor` |
| **[WebApp](WebApp/)** | PostgreSQL + Django — long-term product test database | `cd WebApp && make startwebapp` |

---

## Data handoff (CSV)

After a sensor test run, copy exports into the WebApp import folder:

```bash
cp SensorDataCollector/exports/*.csv WebApp/data/import_pending/
cd WebApp && make import
```

See [WebApp/docs/CSV_IMPORT.md](WebApp/docs/CSV_IMPORT.md).

---

## Documentation

| Guide | Location |
|-------|----------|
| Sensor collector (Grafana, MQTT, sensors) | [SensorDataCollector/README.md](SensorDataCollector/README.md) |
| Product test database (Django) | [WebApp/README.md](WebApp/README.md) |
| Docker Hub images | [SensorDataCollector/docs/DOCKER_HUB.md](SensorDataCollector/docs/DOCKER_HUB.md) · [WebApp/docs/DOCKER_HUB.md](WebApp/docs/DOCKER_HUB.md) |
| CI/CD (auto-publish images) | [docs/CI_CD.md](docs/CI_CD.md) |

---

## License

Licensed under the [MIT License](LICENSE).

Copyright (c) 2026 [Bek Kobro](https://bekcsys.com/about). See [SensorDataCollector/docs/AUTHORS.md](SensorDataCollector/docs/AUTHORS.md).
