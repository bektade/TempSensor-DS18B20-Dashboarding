# Database

## Services and ports

| Service | Port (default) | Purpose |
|---------|----------------|---------|
| `postgres` | 5433 | PostgreSQL 16 |
| `django_web` | 8000 | Django app + admin |
| `pgadmin` | 5050 | DB browser (optional — `cd pgadmin && make start`) |

pgAdmin guide: **[pgadmin/README.md](../pgadmin/README.md)**

## Connect with psql

```bash
cd WebApp
docker compose exec postgres psql -U sauna_user -d sauna_tests
```

From the host (published port):

```bash
psql -h localhost -p 5433 -U sauna_user -d sauna_tests
```

## Example SQL

```sql
-- Latest test runs
SELECT tr.test_run_id, pm.model_name, pu.serial_number, tr.test_date, tr.tester_name
FROM test_runs tr
JOIN product_units pu ON pu.unit_id = tr.unit_id
JOIN product_models pm ON pm.model_id = pu.model_id
ORDER BY tr.test_date DESC
LIMIT 20;

-- Max temperature per sensor for a test
SELECT s.sensor_label, MAX(sr.temperature_f) AS max_f
FROM sensor_readings sr
JOIN sensors s ON s.sensor_id = sr.sensor_id
WHERE sr.test_run_id = 1
GROUP BY s.sensor_label;

-- Import history
SELECT file_name, status, rows_imported, test_run_id, started_at, error_message
FROM import_log
ORDER BY started_at DESC;
```

Reference schema: [sql/postgresql_schema.sql](../sql/postgresql_schema.sql)

## Web UI

- Dashboard — counts and latest tests
- Test run list — filter by model, serial, tester, date
- Test run detail — metadata, readings table, Chart.js plot
- Product unit / model detail pages
