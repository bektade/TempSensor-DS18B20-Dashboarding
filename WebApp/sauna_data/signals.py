from django.db import connection
from django.db.models import Max, Model
from django.db.models.signals import post_delete
from django.dispatch import receiver

from sauna_data.models import ProductModel


def _reset_postgres_pk_sequence(model: type[Model]) -> None:
    max_id = model.objects.aggregate(m=Max(model._meta.pk.name))["m"] or 0
    next_id = max_id + 1
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT setval(
                pg_get_serial_sequence(%s, %s),
                %s,
                false
            )
            """,
            [model._meta.db_table, model._meta.pk.column, next_id],
        )


@receiver(post_delete, sender=ProductModel)
def reset_product_model_id_sequence(sender, instance: ProductModel, **kwargs) -> None:
    if connection.vendor != "postgresql":
        return
    _reset_postgres_pk_sequence(ProductModel)
