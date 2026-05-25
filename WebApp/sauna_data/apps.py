from django.apps import AppConfig


class SaunaDataConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "sauna_data"
    verbose_name = "Product Test Data"

    def ready(self) -> None:
        import sauna_data.signals  # noqa: F401
