# CSV import

## Folder layout

```
WebApp/data/
├── import_pending/     # Drop CSV files here
├── archive/
│   ├── db_migrated/    # Successful imports
│   └── import_failed/    # Failed imports
└── logs/
```

CSV files are never deleted. If an archive filename already exists, a timestamp suffix is added.

## CSV format

Required header (exact column names):

```
timestamp,elapsed_time_in_Min,Timer_in_Min,sensor_id,sensor_label,temperature_c,temperature_f
```

| CSV column | Database column |
|------------|-----------------|
| `timestamp` | `reading_time` |
| `elapsed_time_in_Min` | `elapsed_time_min` |
| `Timer_in_Min` | `timer_remaining_min` |
| `sensor_id` | `sensor_serial` |
| `sensor_label` | `sensor_label` |
| `temperature_c` | `temperature_c` |
| `temperature_f` | `temperature_f` |

## Import CSV (recommended)

```bash
cd WebApp
make startwebapp
cp ../exports/*.csv data/import_pending/
make import
```

Run `make help` in `WebApp/` for the full import workflow printed by the Makefile.

Equivalent: `make startwebapp` then use **Import Pending** at http://localhost:8000/import/pending/

## Other import methods

**Web upload** (metadata form): http://localhost:8000/import/upload/

**Filename metadata** (when model/serial not provided):

`YYYY-MM-DD_HHMMAM_ModelName_SerialNumber.csv`

Example: `2026-05-25_1203PM_Pro22.x_73555-7777.csv`

**Sidecar JSON** (`myfile.meta.json` next to the CSV):

```json
{
  "model_name": "Pro22.x",
  "serial_number": "73555-7777",
  "tester_name": "Lab",
  "supply_voltage": "240",
  "total_amp_draw_start": "12.5",
  "run_duration_min": 90,
  "target_temperature_f": 150,
  "test_location": "Showroom",
  "notes": ""
}
```

**Script inside container:**

```bash
docker compose exec django_web python src/import_csv_to_postgres.py
docker compose exec django_web python src/import_csv_to_postgres.py \
  --model-name "Pro22.x" --serial-number "73555-7777"
```

## Duplicate detection

If the same `file_name` was already imported with `status=success`, the file is skipped (`skipped` in `import_log`; no new `test_run`).

## Failed imports

Failed files move to `data/archive/import_failed/`. Fix the CSV or metadata, copy back to `import_pending/`, run `make import` again.

## Import log

Each run records `test_run_id`, row count, sensors detected, max temperature per sensor, archive path, and status. View in Django admin under **Import log**.
