import json
from collections import defaultdict
from decimal import Decimal

from django.conf import settings
from django.db.models import Count, Max
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from sauna_data.forms import CsvImportForm, ProductModelFilterForm, TestRunFilterForm
from sauna_data.models import ImportLog, PowerBoxType, ProductModel, ProductUnit, SensorReading, TestRun
from sauna_data.services.csv_import import import_csv_file, scan_and_import_pending


def _minutes_to_target_f(test_run: TestRun, target_f: float = 150.0) -> dict[str, int | None]:
    readings = (
        SensorReading.objects.filter(test_run=test_run)
        .select_related("sensor")
        .order_by("elapsed_time_min", "reading_time")
    )
    reached: dict[str, int | None] = {}
    seen: dict[str, bool] = {}
    for reading in readings:
        label = reading.sensor.sensor_label or reading.sensor.sensor_serial
        if seen.get(label):
            continue
        temp_f = float(reading.temperature_f or 0)
        if temp_f >= target_f:
            reached[label] = reading.elapsed_time_min
            seen[label] = True
    for reading in readings:
        label = reading.sensor.sensor_label or reading.sensor.sensor_serial
        if label not in reached:
            reached[label] = None
    return reached


def _powerbox_model_groups() -> list[dict[str, object]]:
    groups: list[dict[str, object]] = []
    for powerbox_type in PowerBoxType.objects.order_by("name"):
        models = (
            ProductModel.objects.filter(units__powerbox_type=powerbox_type)
            .distinct()
            .order_by("model_name")
        )
        groups.append({"powerbox_type": powerbox_type, "models": models})
    return groups


def dashboard(request: HttpRequest) -> HttpResponse:
    latest_tests = (
        TestRun.objects.select_related("unit", "unit__model")
        .order_by("-test_date")[:10]
    )
    context = {
        "total_test_runs": TestRun.objects.count(),
        "total_models": ProductModel.objects.count(),
        "total_units": ProductUnit.objects.count(),
        "latest_tests": latest_tests,
    }
    return render(request, "sauna_data/dashboard.html", context)


def test_run_list(request: HttpRequest) -> HttpResponse:
    form = TestRunFilterForm(request.GET or None)
    queryset = TestRun.objects.select_related("unit", "unit__model").order_by("-test_date")
    if form.is_valid():
        if form.cleaned_data.get("model_name"):
            queryset = queryset.filter(
                unit__model__model_name__icontains=form.cleaned_data["model_name"]
            )
        if form.cleaned_data.get("serial_number"):
            queryset = queryset.filter(
                unit__serial_number__icontains=form.cleaned_data["serial_number"]
            )
        if form.cleaned_data.get("tester"):
            queryset = queryset.filter(
                tester_name__icontains=form.cleaned_data["tester"]
            )
        if form.cleaned_data.get("date_from"):
            queryset = queryset.filter(test_date__date__gte=form.cleaned_data["date_from"])
        if form.cleaned_data.get("date_to"):
            queryset = queryset.filter(test_date__date__lte=form.cleaned_data["date_to"])
    return render(
        request,
        "sauna_data/test_run_list.html",
        {"test_runs": queryset, "form": form},
    )


def test_run_detail(request: HttpRequest, test_run_id: int) -> HttpResponse:
    test_run = get_object_or_404(
        TestRun.objects.select_related("unit", "unit__model"),
        test_run_id=test_run_id,
    )
    max_rows = (
        SensorReading.objects.filter(test_run=test_run)
        .values("sensor__sensor_label", "sensor__sensor_serial")
        .annotate(max_f=Max("temperature_f"), max_c=Max("temperature_c"))
    )
    target_f = float(test_run.target_temperature_f or 150)
    minutes_to_target = _minutes_to_target_f(test_run, target_f)
    max_by_sensor = []
    for row in max_rows:
        label = row["sensor__sensor_label"] or row["sensor__sensor_serial"]
        max_by_sensor.append(
            {
                "label": label,
                "max_f": row["max_f"],
                "max_c": row["max_c"],
                "minutes_to_target": minutes_to_target.get(label),
            }
        )
    readings = (
        SensorReading.objects.filter(test_run=test_run)
        .select_related("sensor")
        .order_by("elapsed_time_min", "sensor__sensor_label")[:500]
    )
    chart_series: dict[str, list[dict[str, float]]] = defaultdict(list)
    for reading in SensorReading.objects.filter(test_run=test_run).select_related("sensor"):
        label = reading.sensor.sensor_label or reading.sensor.sensor_serial
        chart_series[label].append(
            {
                "x": reading.elapsed_time_min,
                "y": float(reading.temperature_f or 0),
            }
        )
    context = {
        "test_run": test_run,
        "max_by_sensor": max_by_sensor,
        "readings": readings,
        "chart_series_json": json.dumps(chart_series),
        "target_temperature_f": target_f,
    }
    return render(request, "sauna_data/test_run_detail.html", context)


def product_model_list(request: HttpRequest) -> HttpResponse:
    form = ProductModelFilterForm(request.GET or None)
    queryset = ProductModel.objects.annotate(unit_count=Count("units")).order_by("model_name")
    if form.is_valid():
        if form.cleaned_data.get("supplier"):
            queryset = queryset.filter(supplier=form.cleaned_data["supplier"])
        if form.cleaned_data.get("rated_voltage"):
            queryset = queryset.filter(
                rated_voltage=Decimal(form.cleaned_data["rated_voltage"])
            )
        if form.cleaned_data.get("rated_power_watts"):
            queryset = queryset.filter(
                rated_power_watts=Decimal(form.cleaned_data["rated_power_watts"])
            )
        if form.cleaned_data.get("orders"):
            queryset = queryset.filter(unit_count=int(form.cleaned_data["orders"]))
    return render(
        request,
        "sauna_data/product_model_list.html",
        {
            "product_models": queryset,
            "form": form,
            "powerbox_model_groups": _powerbox_model_groups(),
        },
    )


def product_unit_list(request: HttpRequest) -> HttpResponse:
    units = (
        ProductUnit.objects.select_related("model", "powerbox_type")
        .annotate(test_count=Count("test_runs"))
        .order_by("model__model_name", "serial_number")
    )
    return render(
        request,
        "sauna_data/product_unit_list.html",
        {"product_units": units},
    )


def product_unit_detail(request: HttpRequest, unit_id: int) -> HttpResponse:
    unit = get_object_or_404(
        ProductUnit.objects.select_related("model", "powerbox_type"), unit_id=unit_id
    )
    test_runs = unit.test_runs.order_by("-test_date")
    return render(
        request,
        "sauna_data/product_unit_detail.html",
        {"unit": unit, "test_runs": test_runs},
    )


def product_model_detail(request: HttpRequest, model_id: int) -> HttpResponse:
    model = get_object_or_404(ProductModel, model_id=model_id)
    units = model.units.annotate(test_count=Count("test_runs")).order_by("serial_number")
    test_runs = (
        TestRun.objects.filter(unit__model=model)
        .select_related("unit")
        .order_by("-test_date")
    )
    return render(
        request,
        "sauna_data/product_model_detail.html",
        {"model": model, "units": units, "test_runs": test_runs},
    )


def import_home(request: HttpRequest) -> HttpResponse:
    return redirect("import_upload")


def import_upload(request: HttpRequest) -> HttpResponse:
    summary = None
    form = CsvImportForm()

    if request.method == "POST":
        form = CsvImportForm(request.POST, request.FILES)
        if form.is_valid():
            settings.IMPORT_PENDING_DIR.mkdir(parents=True, exist_ok=True)
            upload_name = request.FILES["csv_file"].name
            pending_path = settings.IMPORT_PENDING_DIR / upload_name
            with pending_path.open("wb") as destination:
                for chunk in request.FILES["csv_file"].chunks():
                    destination.write(chunk)
            summary = import_csv_file(pending_path, metadata=form.to_metadata())

    return render(
        request,
        "sauna_data/import_upload.html",
        {"import_tab": "upload", "form": form, "summary": summary},
    )


def import_pending(request: HttpRequest) -> HttpResponse:
    batch_summaries = None
    if request.method == "POST":
        batch_summaries = scan_and_import_pending()

    pending_files = sorted(settings.IMPORT_PENDING_DIR.glob("*.csv"))
    return render(
        request,
        "sauna_data/import_pending.html",
        {
            "import_tab": "pending",
            "pending_files": pending_files,
            "batch_summaries": batch_summaries,
        },
    )


def import_recent(request: HttpRequest) -> HttpResponse:
    recent_imports = ImportLog.objects.order_by("-started_at")[:20]
    return render(
        request,
        "sauna_data/import_recent.html",
        {"import_tab": "recent", "recent_imports": recent_imports},
    )
