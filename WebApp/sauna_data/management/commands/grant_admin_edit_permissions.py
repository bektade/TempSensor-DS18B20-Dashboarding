from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from sauna_data.models import (
    ImportLog,
    PowerBoxType,
    ProductModel,
    ProductUnit,
    Sensor,
    SensorReading,
    TestRun,
)

EDIT_MODELS = (
    ProductModel,
    ProductUnit,
    PowerBoxType,
    TestRun,
    Sensor,
    SensorReading,
    ImportLog,
)


class Command(BaseCommand):
    help = "Grant add/change/delete permissions on app models for a staff user (enables editing in Django admin)."

    def add_arguments(self, parser):
        parser.add_argument("username", help="Django username (must have Staff status)")

    def handle(self, *args, **options):
        User = get_user_model()
        username = options["username"]
        user = User.objects.filter(username=username).first()
        if not user:
            self.stderr.write(self.style.ERROR(f"User not found: {username}"))
            return

        if not user.is_staff:
            user.is_staff = True
            user.save(update_fields=["is_staff"])
            self.stdout.write(self.style.WARNING(f"Enabled staff status for {username}"))

        perms = []
        for model in EDIT_MODELS:
            content_type = ContentType.objects.get_for_model(model)
            for action in ("add", "change", "delete", "view"):
                codename = f"{action}_{model._meta.model_name}"
                permission = Permission.objects.filter(
                    content_type=content_type, codename=codename
                ).first()
                if permission:
                    perms.append(permission)

        user.user_permissions.add(*perms)
        self.stdout.write(
            self.style.SUCCESS(
                f"Granted {len(perms)} permissions to {username}. "
                "They can add, change, and delete records in /admin/."
            )
        )
