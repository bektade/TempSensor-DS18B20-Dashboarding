CSV migration/archive requirements:

Create an automated CSV-to-PostgreSQL migration system.

Purpose:
The system should automatically import sauna test CSV files into PostgreSQL and archive the imported CSV files afterward to reduce CSV clutter and preserve historical raw files.

Folder structure:

WebApp/
├── data/
│   ├── import_pending/
│   ├── archive/
│   │   ├── db_migrated/
│   │   └── import_failed/
│   └── logs/

Behavior:
1. CSV files placed inside:

data/import_pending/

should be automatically importable into PostgreSQL using either:
- Django management command
- background import service
- manual admin import button

2. After successful database import:
Move CSV file to:

data/archive/db_migrated/

3. If import fails:
Move CSV file to:

data/archive/import_failed/

4. Never delete CSV files automatically.

5. Preserve original filenames.

6. Add timestamp suffix during archive if duplicate filename already exists.

Import log tracking:
Create additional PostgreSQL table:

import_log

Schema:

CREATE TABLE import_log (
    import_id BIGSERIAL PRIMARY KEY,
    file_name TEXT NOT NULL,
    original_file_path TEXT,
    archived_file_path TEXT,
    test_run_id BIGINT REFERENCES test_runs(test_run_id),
    status TEXT NOT NULL,
    rows_imported INT DEFAULT 0,
    sensors_detected INT DEFAULT 0,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT
);

Add indexes:

CREATE INDEX idx_import_log_file_name
ON import_log(file_name);

CREATE INDEX idx_import_log_status
ON import_log(status);

Duplicate import prevention:
Before importing a CSV:
- check whether the same file_name was already successfully imported
- if already imported:
  - skip import
  - log warning
  - prevent duplicate test_run creation

CSV import script:
Create:

src/import_csv_to_postgres.py

Requirements:
- scan data/import_pending/
- import all CSV files found
- validate CSV structure
- validate required columns
- create/reuse product model
- create/reuse product unit
- create/reuse sensors
- create new test_run
- bulk insert sensor_readings efficiently
- log import result into import_log
- archive CSV after processing

Current CSV format to support exactly:

timestamp,elapsed_time_in_Min,Timer_in_Min,sensor_id,sensor_label,temperature_c,temperature_f

Example:

timestamp,elapsed_time_in_Min,Timer_in_Min,sensor_id,sensor_label,temperature_c,temperature_f
2026-05-25 12:03:09,0,90,28-0000004a6df4,Sensor1,24.1,75.4
2026-05-25 12:03:09,0,90,28-00000048c1df,Sensor2,24.1,75.4

CSV mapping:

timestamp → reading_time
elapsed_time_in_Min → elapsed_time_min
Timer_in_Min → timer_remaining_min
sensor_id → sensor_serial
sensor_label → sensor_label
temperature_c → temperature_c
temperature_f → temperature_f

Import summary:
After each import display:

- CSV file name
- test_run_id
- rows imported
- sensors detected
- max temperature per sensor
- archive path
- import duration
- success/failure status

Performance requirements:
- use PostgreSQL bulk inserts where possible
- optimize for large CSV imports
- support future scaling to millions of sensor readings

Django admin:
Add admin page for import_log table.

Allow viewing:
- imported files
- failed imports
- import timestamps
- error messages
- linked test_run_id

README updates:
Document:
- how CSV import works
- how archive folders work
- how failed imports are handled
- how to rerun failed imports
- how duplicate detection works
