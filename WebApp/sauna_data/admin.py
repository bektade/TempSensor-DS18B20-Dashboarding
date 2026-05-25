from django.contrib import admin

from sauna_data.models import (
    ImportLog,
    PowerBoxType,
    ProductModel,
    ProductUnit,
    Sensor,
    SensorReading,
    TestRun,
)


class EditableModelAdmin(admin.ModelAdmin):
    """Allow add, change, and delete for staff with the default model permissions."""

    def has_view_permission(self, request, obj=None):
        return request.user.is_active and (
            request.user.is_superuser or super().has_view_permission(request, obj)
        )

    def has_add_permission(self, request):
        return request.user.is_active and (
            request.user.is_superuser or super().has_add_permission(request)
        )

    def has_change_permission(self, request, obj=None):
        return request.user.is_active and (
            request.user.is_superuser or super().has_change_permission(request, obj)
        )

    def has_delete_permission(self, request, obj=None):
        return request.user.is_active and (
            request.user.is_superuser or super().has_delete_permission(request, obj)
        )


@admin.register(ProductModel)
class ProductModelAdmin(EditableModelAdmin):
    list_display = ("model_id", "model_name", "supplier", "rated_voltage", "created_at")
    list_display_links = ("model_name",)
    list_filter = ("supplier",)
    search_fields = ("model_name",)
    ordering = ("model_name",)
    readonly_fields = ("model_id", "created_at")
    fieldsets = (
        (None, {"fields": ("model_name", "supplier")}),
        ("Specifications", {"fields": ("rated_voltage", "rated_power_watts", "notes")}),
        ("System", {"fields": ("model_id", "created_at"), "classes": ("collapse",)}),
    )


@admin.register(PowerBoxType)
class PowerBoxTypeAdmin(EditableModelAdmin):
    list_display = ("powerbox_type_id", "name")
    list_display_links = ("name",)
    search_fields = ("name",)
    ordering = ("name",)
    readonly_fields = ("powerbox_type_id",)


@admin.register(ProductUnit)
class ProductUnitAdmin(EditableModelAdmin):
    list_display = (
        "unit_id",
        "serial_number",
        "model",
        "powerbox_type",
        "wattage",
        "created_at",
    )
    list_display_links = ("serial_number",)
    list_filter = ("model", "model__supplier", "powerbox_type")
    search_fields = ("serial_number", "model__model_name", "powerbox_type__name")
    ordering = ("serial_number",)
    readonly_fields = ("unit_id", "created_at")
    fieldsets = (
        (
            None,
            {"fields": ("serial_number", "model", "powerbox_type", "wattage", "notes")},
        ),
        ("System", {"fields": ("unit_id", "created_at"), "classes": ("collapse",)}),
    )


@admin.register(TestRun)
class TestRunAdmin(EditableModelAdmin):
    list_display = (
        "test_run_id",
        "unit",
        "test_date",
        "tester_name",
        "run_duration_min",
        "created_at",
    )
    list_display_links = ("test_run_id",)
    list_filter = ("test_date", "tester_name", "unit__model")
    search_fields = (
        "tester_name",
        "unit__serial_number",
        "unit__model__model_name",
        "notes",
    )
    date_hierarchy = "test_date"
    ordering = ("-test_date",)
    readonly_fields = ("test_run_id", "created_at")
    fieldsets = (
        (None, {"fields": ("unit", "test_date", "tester_name", "test_location")}),
        (
            "Test parameters",
            {
                "fields": (
                    "supply_voltage",
                    "total_amp_draw_start",
                    "run_duration_min",
                    "target_temperature_f",
                    "notes",
                )
            },
        ),
        ("System", {"fields": ("test_run_id", "created_at"), "classes": ("collapse",)}),
    )


@admin.register(Sensor)
class SensorAdmin(EditableModelAdmin):
    list_display = ("sensor_id", "sensor_serial", "sensor_label", "sensor_type")
    list_display_links = ("sensor_serial",)
    search_fields = ("sensor_serial", "sensor_label")
    readonly_fields = ("sensor_id", "created_at")
    fieldsets = (
        (None, {"fields": ("sensor_serial", "sensor_label", "sensor_type", "notes")}),
        ("System", {"fields": ("sensor_id", "created_at"), "classes": ("collapse",)}),
    )


@admin.register(SensorReading)
class SensorReadingAdmin(EditableModelAdmin):
    list_display = (
        "reading_id",
        "test_run",
        "sensor",
        "reading_time",
        "elapsed_time_min",
        "temperature_f",
    )
    list_display_links = ("reading_id",)
    list_filter = ("sensor",)
    search_fields = ("test_run__test_run_id", "sensor__sensor_serial")
    date_hierarchy = "reading_time"
    ordering = ("-reading_time",)
    readonly_fields = ("reading_id", "created_at")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "test_run",
                    "sensor",
                    "reading_time",
                    "elapsed_time_min",
                    "timer_remaining_min",
                    "temperature_c",
                    "temperature_f",
                )
            },
        ),
        ("System", {"fields": ("reading_id", "created_at"), "classes": ("collapse",)}),
    )


@admin.register(ImportLog)
class ImportLogAdmin(EditableModelAdmin):
    list_display = (
        "import_id",
        "file_name",
        "status",
        "test_run",
        "rows_imported",
        "sensors_detected",
        "started_at",
        "completed_at",
    )
    list_display_links = ("file_name",)
    list_filter = ("status",)
    search_fields = ("file_name", "error_message")
    readonly_fields = (
        "import_id",
        "file_name",
        "original_file_path",
        "archived_file_path",
        "rows_imported",
        "sensors_detected",
        "started_at",
        "completed_at",
    )
    fieldsets = (
        (None, {"fields": ("file_name", "status", "test_run", "error_message")}),
        (
            "Import details",
            {
                "fields": (
                    "rows_imported",
                    "sensors_detected",
                    "original_file_path",
                    "archived_file_path",
                    "started_at",
                    "completed_at",
                )
            },
        ),
        ("System", {"fields": ("import_id",), "classes": ("collapse",)}),
    )
    ordering = ("-started_at",)
