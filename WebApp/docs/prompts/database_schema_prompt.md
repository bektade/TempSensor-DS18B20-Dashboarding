Create a separate Docker-based PostgreSQL + Django web application for long-term sauna test data storage and exploration.

Important context:
I already have an existing Docker system for MQTT, Grafana, and InfluxDB real-time monitoring. Do NOT integrate this new database system with the existing MQTT/Grafana/InfluxDB stack.

This new system should be completely separate and dedicated to:
- long-term sauna test data storage
- CSV import
- metadata management
- historical test exploration
- Django-based web application
- reducing CSV file clutter

Purpose:
The goal is to avoid manually managing many CSV files. Each sauna test run generates a CSV file with temperature readings from multiple DS18B20 sensors. The Django app should import the CSV, associate it with metadata, store everything in PostgreSQL, and allow searching/filtering/exploring test data later.

Current CSV format:

timestamp,elapsed_time_in_Min,Timer_in_Min,sensor_id,sensor_label,temperature_c,temperature_f

Example:

timestamp,elapsed_time_in_Min,Timer_in_Min,sensor_id,sensor_label,temperature_c,temperature_f
2026-05-25 12:03:09,0,90,28-0000004a6df4,Sensor1,24.1,75.4
2026-05-25 12:03:09,0,90,28-00000048c1df,Sensor2,24.1,75.4

Column meaning:
- timestamp = date and time of sensor reading
- elapsed_time_in_Min = elapsed test time in minutes
- Timer_in_Min = sauna timer remaining in minutes
- sensor_id = DS18B20 sensor serial/address
- sensor_label = simple label such as Sensor1, Sensor2
- temperature_c = temperature in Celsius
- temperature_f = temperature in Fahrenheit

Important:
The Django CSV import tool must support this exact current CSV format.

Map CSV columns into the database as follows:

timestamp → reading_time
elapsed_time_in_Min → elapsed_time_min
Timer_in_Min → timer_remaining_min
sensor_id → sensor_serial
sensor_label → sensor_label
temperature_c → temperature_c
temperature_f → temperature_f

Test metadata:
Each CSV import should also collect metadata:

- model_name
- serial_number
- test_date
- tester_name
- supply_voltage
- total_amp_draw_start
- run_duration_min
- target_temperature_f
- test_location
- notes

System architecture:
Create a completely separate project folder such as:

sauna-test-data-platform/

The project should include:
- PostgreSQL database
- Django web application
- Docker Compose setup
- CSV import functionality
- basic web interface for exploring test data

Do not include:
- MQTT
- InfluxDB
- existing Grafana stack
- real-time telemetry integration

Required Docker services:
1. postgres
2. django_web

Optional:
3. pgadmin

Database design:
Use a normalized PostgreSQL schema with these tables:

1. product_models
Purpose:
Stores sauna model information.

Columns:
- model_id SERIAL PRIMARY KEY
- model_name TEXT UNIQUE NOT NULL
- rated_voltage NUMERIC(6,2)
- rated_power_watts NUMERIC(10,2)
- notes TEXT
- created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

2. product_units
Purpose:
Stores physical sauna units.

Columns:
- unit_id SERIAL PRIMARY KEY
- model_id INT NOT NULL REFERENCES product_models(model_id)
- serial_number TEXT UNIQUE NOT NULL
- notes TEXT
- created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

3. test_runs
Purpose:
Stores one row per sauna test session.

Columns:
- test_run_id BIGSERIAL PRIMARY KEY
- unit_id INT NOT NULL REFERENCES product_units(unit_id)
- test_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
- tester_name TEXT
- supply_voltage NUMERIC(6,2)
- total_amp_draw_start NUMERIC(6,2)
- run_duration_min INT DEFAULT 90
- target_temperature_f NUMERIC(5,2) DEFAULT 150
- test_location TEXT
- notes TEXT
- created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

4. sensors
Purpose:
Stores sensor metadata.

Columns:
- sensor_id SERIAL PRIMARY KEY
- sensor_serial TEXT UNIQUE NOT NULL
- sensor_label TEXT
- sensor_type TEXT DEFAULT 'DS18B20'
- notes TEXT
- created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

5. sensor_readings
Purpose:
Stores raw time-series temperature data.

Columns:
- reading_id BIGSERIAL PRIMARY KEY
- test_run_id BIGINT NOT NULL REFERENCES test_runs(test_run_id) ON DELETE CASCADE
- sensor_id INT NOT NULL REFERENCES sensors(sensor_id)
- reading_time TIMESTAMP NOT NULL
- elapsed_time_min INT NOT NULL
- timer_remaining_min INT
- temperature_c NUMERIC(6,2)
- temperature_f NUMERIC(6,2)
- created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

Relationships:
- One product model can have many product units.
- One physical unit can have many test runs.
- One test run can have many sensor readings.
- One sensor can appear in many test runs.

Important design rule:
Do NOT store:
- model_name
- serial_number
- voltage
- tester
- notes
- metadata

inside every sensor reading row.

Keep metadata normalized and separate from raw sensor readings.

Indexes:
Add indexes for:
- product_models.model_name
- product_units.serial_number
- product_units.model_id
- test_runs.unit_id
- test_runs.test_date
- sensor_readings.test_run_id
- sensor_readings.sensor_id
- sensor_readings.reading_time
- sensor_readings(test_run_id, reading_time)

Django requirements:
Create Django models for:
- ProductModel
- ProductUnit
- TestRun
- Sensor
- SensorReading

Configure Django admin so I can:
- browse models
- browse sauna units
- browse test runs
- browse sensors
- browse sensor readings
- search by model_name
- search by serial_number
- filter by tester
- filter by date

CSV import requirements:
Create a Django management command or upload page to import CSV files.

The import workflow should:
1. Accept CSV file upload.
2. Prompt for metadata:
   - model_name
   - serial_number
   - tester_name
   - supply_voltage
   - total_amp_draw_start
   - run_duration_min
   - target_temperature_f
   - test_location
   - notes

3. Create or reuse:
   - product model
   - product unit
   - sensors

4. Create a new test_run.
5. Import all CSV rows into sensor_readings.
6. Validate required CSV columns.
7. Display import summary:
   - test_run_id
   - rows imported
   - sensors detected
   - max temperature per sensor
   - reading time range

Web app pages:
Create simple Django pages for:

1. Dashboard
Show:
- total number of test runs
- total product models
- total product units
- latest imported tests

2. Test Run List
Allow filtering by:
- model_name
- serial_number
- tester
- date

3. Test Run Detail Page
Show:
- metadata
- sensors used
- temperature table
- max temperature
- time to reach 150°F
- temperature chart

4. Product Unit Detail
Show:
- serial number
- model name
- all related test runs

5. Product Model Detail
Show:
- model name
- all product units
- all related tests

Charting:
Use a simple charting library such as Chart.js.

Plot:
- temperature_f vs elapsed_time_min
- one line per sensor_label

Keep charting simple. This does not replace Grafana.

Docker requirements:
Create:
- docker-compose.yml
- Dockerfile
- .env.example

Use:
- PostgreSQL
- persistent Docker volume
- environment variables
- automatic migrations

Deliverables:
- docker-compose.yml
- Dockerfile
- .env.example
- requirements.txt
- PostgreSQL schema
- Django models
- Django admin configuration
- CSV import tool
- HTML templates
- Chart.js integration
- README.md
- setup documentation

README should include:
- how to start Docker containers
- how to create Django superuser
- how to run migrations
- how to import CSV files
- how to access the Django app
- how to connect to PostgreSQL
- example SQL queries

Important:
This project is a separate long-term engineering test data platform and must remain independent from the existing MQTT/Grafana/InfluxDB real-time monitoring system.
