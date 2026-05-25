-- Reference schema for product test data platform (managed by Django migrations).

CREATE TABLE product_models (
    model_id SERIAL PRIMARY KEY,
    model_name TEXT UNIQUE NOT NULL,
    rated_voltage NUMERIC(6,2),
    rated_power_watts NUMERIC(10,2),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_product_models_model_name ON product_models(model_name);

CREATE TABLE product_units (
    unit_id SERIAL PRIMARY KEY,
    model_id INT NOT NULL REFERENCES product_models(model_id),
    serial_number TEXT UNIQUE NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_product_units_serial_number ON product_units(serial_number);
CREATE INDEX idx_product_units_model_id ON product_units(model_id);

CREATE TABLE test_runs (
    test_run_id BIGSERIAL PRIMARY KEY,
    unit_id INT NOT NULL REFERENCES product_units(unit_id),
    test_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    tester_name TEXT,
    supply_voltage NUMERIC(6,2),
    total_amp_draw_start NUMERIC(6,2),
    run_duration_min INT DEFAULT 90,
    target_temperature_f NUMERIC(5,2) DEFAULT 150,
    test_location TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_test_runs_unit_id ON test_runs(unit_id);
CREATE INDEX idx_test_runs_test_date ON test_runs(test_date);

CREATE TABLE sensors (
    sensor_id SERIAL PRIMARY KEY,
    sensor_serial TEXT UNIQUE NOT NULL,
    sensor_label TEXT,
    sensor_type TEXT DEFAULT 'DS18B20',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sensor_readings (
    reading_id BIGSERIAL PRIMARY KEY,
    test_run_id BIGINT NOT NULL REFERENCES test_runs(test_run_id) ON DELETE CASCADE,
    sensor_id INT NOT NULL REFERENCES sensors(sensor_id),
    reading_time TIMESTAMP NOT NULL,
    elapsed_time_min INT NOT NULL,
    timer_remaining_min INT,
    temperature_c NUMERIC(6,2),
    temperature_f NUMERIC(6,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_sensor_readings_test_run_id ON sensor_readings(test_run_id);
CREATE INDEX idx_sensor_readings_sensor_id ON sensor_readings(sensor_id);
CREATE INDEX idx_sensor_readings_reading_time ON sensor_readings(reading_time);
CREATE INDEX idx_sensor_readings_test_run_time ON sensor_readings(test_run_id, reading_time);

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
CREATE INDEX idx_import_log_file_name ON import_log(file_name);
CREATE INDEX idx_import_log_status ON import_log(status);
