from decimal import Decimal

from django import forms
from django.db.models import Count

from sauna_data.models import ProductModel
from sauna_data.services.csv_import import ImportMetadata


class CsvImportForm(forms.Form):
    csv_file = forms.FileField(label="CSV file")
    model_name = forms.ChoiceField(label="Model name", choices=[])
    serial_number = forms.CharField(max_length=200)
    tester_name = forms.CharField(max_length=200, required=False)
    supply_voltage = forms.DecimalField(
        max_digits=6, decimal_places=2, required=False, min_value=0
    )
    total_amp_draw_start = forms.DecimalField(
        max_digits=6, decimal_places=2, required=False, min_value=0
    )
    run_duration_min = forms.IntegerField(initial=90, min_value=1)
    target_temperature_f = forms.DecimalField(
        max_digits=5, decimal_places=2, initial=Decimal("150"), min_value=0
    )
    test_location = forms.CharField(max_length=200, required=False)
    notes = forms.CharField(widget=forms.Textarea, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        model_names = ProductModel.objects.order_by("model_name").values_list(
            "model_name", flat=True
        )
        self.fields["model_name"].choices = [("", "Select a product model")] + [
            (name, name) for name in model_names
        ]

    def to_metadata(self) -> ImportMetadata:
        cleaned = self.cleaned_data
        return ImportMetadata(
            model_name=cleaned["model_name"],
            serial_number=cleaned["serial_number"],
            tester_name=cleaned.get("tester_name", ""),
            supply_voltage=cleaned.get("supply_voltage"),
            total_amp_draw_start=cleaned.get("total_amp_draw_start"),
            run_duration_min=cleaned.get("run_duration_min", 90),
            target_temperature_f=cleaned.get("target_temperature_f") or Decimal("150"),
            test_location=cleaned.get("test_location", ""),
            notes=cleaned.get("notes", ""),
        )


class TestRunFilterForm(forms.Form):
    model_name = forms.CharField(required=False)
    serial_number = forms.CharField(required=False)
    tester = forms.CharField(required=False)
    date_from = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))
    date_to = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))


class ProductModelFilterForm(forms.Form):
    supplier = forms.ChoiceField(required=False, label="Supplier")
    rated_voltage = forms.ChoiceField(required=False, label="Voltage")
    rated_power_watts = forms.ChoiceField(required=False, label="Wattage")
    orders = forms.ChoiceField(required=False, label="Orders")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["supplier"].choices = [("", "All")] + list(ProductModel.Supplier.choices)
        voltages = (
            ProductModel.objects.exclude(rated_voltage__isnull=True)
            .values_list("rated_voltage", flat=True)
            .distinct()
            .order_by("rated_voltage")
        )
        self.fields["rated_voltage"].choices = [("", "All")] + [
            (str(v), str(v)) for v in voltages
        ]
        wattages = (
            ProductModel.objects.exclude(rated_power_watts__isnull=True)
            .values_list("rated_power_watts", flat=True)
            .distinct()
            .order_by("rated_power_watts")
        )
        self.fields["rated_power_watts"].choices = [("", "All")] + [
            (str(w), str(w)) for w in wattages
        ]
        order_counts = (
            ProductModel.objects.annotate(unit_count=Count("units"))
            .values_list("unit_count", flat=True)
            .distinct()
            .order_by("unit_count")
        )
        self.fields["orders"].choices = [("", "All")] + [
            (str(count), str(count)) for count in order_counts
        ]
