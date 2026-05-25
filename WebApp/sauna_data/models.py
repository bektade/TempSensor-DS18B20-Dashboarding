from django.db import models


class ProductModel(models.Model):
    class Supplier(models.TextChoices):
        GLOBAL = "GLOBAL", "GLOBAL"
        ROYAL = "ROYAL", "ROYAL"
        SMARTMAK = "SMARTMAK", "SMARTMAK"

    model_id = models.AutoField(primary_key=True)
    model_name = models.TextField(unique=True)
    supplier = models.CharField(
        max_length=20,
        choices=Supplier.choices,
        blank=True,
        default="",
    )
    rated_voltage = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    rated_power_watts = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "product_models"
        indexes = [
            models.Index(fields=["model_name"], name="idx_product_models_model_name"),
        ]

    def __str__(self) -> str:
        return self.model_name


class PowerBoxType(models.Model):
    powerbox_type_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = "powerbox_types"
        verbose_name = "Power box type"
        verbose_name_plural = "Power box types"

    def __str__(self) -> str:
        return self.name


class ProductUnit(models.Model):
    unit_id = models.AutoField(primary_key=True)
    model = models.ForeignKey(
        ProductModel,
        on_delete=models.PROTECT,
        related_name="units",
        db_column="model_id",
    )
    serial_number = models.TextField(unique=True)
    powerbox_type = models.ForeignKey(
        PowerBoxType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="units",
        db_column="powerbox_type_id",
    )
    wattage = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "product_units"
        indexes = [
            models.Index(fields=["serial_number"], name="idx_product_units_serial"),
            models.Index(fields=["model"], name="idx_product_units_model_id"),
        ]

    def __str__(self) -> str:
        return self.serial_number

    @property
    def display_wattage(self):
        if self.wattage is not None:
            return self.wattage
        return self.model.rated_power_watts


class TestRun(models.Model):
    test_run_id = models.BigAutoField(primary_key=True, verbose_name="TestID")
    unit = models.ForeignKey(
        ProductUnit,
        on_delete=models.PROTECT,
        related_name="test_runs",
        db_column="unit_id",
    )
    test_date = models.DateTimeField()
    tester_name = models.TextField(blank=True, default="")
    supply_voltage = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True
    )
    total_amp_draw_start = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True
    )
    run_duration_min = models.IntegerField(default=90)
    target_temperature_f = models.DecimalField(
        max_digits=5, decimal_places=2, default=150
    )
    test_location = models.TextField(blank=True, default="")
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "test_runs"
        indexes = [
            models.Index(fields=["unit"], name="idx_test_runs_unit_id"),
            models.Index(fields=["test_date"], name="idx_test_runs_test_date"),
        ]

    def __str__(self) -> str:
        return f"TestRun {self.test_run_id} ({self.test_date:%Y-%m-%d})"


class Sensor(models.Model):
    sensor_id = models.AutoField(primary_key=True)
    sensor_serial = models.TextField(unique=True)
    sensor_label = models.TextField(blank=True, default="")
    sensor_type = models.TextField(default="DS18B20")
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "sensors"

    def __str__(self) -> str:
        return self.sensor_label or self.sensor_serial


class SensorReading(models.Model):
    reading_id = models.BigAutoField(primary_key=True)
    test_run = models.ForeignKey(
        TestRun,
        on_delete=models.CASCADE,
        related_name="readings",
        db_column="test_run_id",
    )
    sensor = models.ForeignKey(
        Sensor,
        on_delete=models.PROTECT,
        related_name="readings",
        db_column="sensor_id",
    )
    reading_time = models.DateTimeField()
    elapsed_time_min = models.IntegerField()
    timer_remaining_min = models.IntegerField(null=True, blank=True)
    temperature_c = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    temperature_f = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "sensor_readings"
        indexes = [
            models.Index(fields=["test_run"], name="idx_sensor_readings_test_run"),
            models.Index(fields=["sensor"], name="idx_sensor_readings_sensor"),
            models.Index(fields=["reading_time"], name="idx_sensor_readings_time"),
            models.Index(
                fields=["test_run", "reading_time"],
                name="idx_sensor_readings_run_time",
            ),
        ]


class ImportLog(models.Model):
    STATUS_PENDING = "pending"
    STATUS_SUCCESS = "success"
    STATUS_FAILED = "failed"
    STATUS_SKIPPED = "skipped"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_SUCCESS, "Success"),
        (STATUS_FAILED, "Failed"),
        (STATUS_SKIPPED, "Skipped"),
    ]

    import_id = models.BigAutoField(primary_key=True)
    file_name = models.TextField()
    original_file_path = models.TextField(blank=True, default="")
    archived_file_path = models.TextField(blank=True, default="")
    test_run = models.ForeignKey(
        TestRun,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="import_logs",
        db_column="test_run_id",
    )
    status = models.TextField(choices=STATUS_CHOICES)
    rows_imported = models.IntegerField(default=0)
    sensors_detected = models.IntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True, default="")

    class Meta:
        db_table = "import_log"
        indexes = [
            models.Index(fields=["file_name"], name="idx_import_log_file_name"),
            models.Index(fields=["status"], name="idx_import_log_status"),
        ]

    def __str__(self) -> str:
        return f"{self.file_name} ({self.status})"
