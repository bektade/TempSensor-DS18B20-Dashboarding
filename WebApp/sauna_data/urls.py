from django.urls import path

from sauna_data import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("tests/", views.test_run_list, name="test_run_list"),
    path("tests/<int:test_run_id>/", views.test_run_detail, name="test_run_detail"),
    path("models/", views.product_model_list, name="product_model_list"),
    path("models/<int:model_id>/", views.product_model_detail, name="product_model_detail"),
    path("units/", views.product_unit_list, name="product_unit_list"),
    path("units/<int:unit_id>/", views.product_unit_detail, name="product_unit_detail"),
    path("import/", views.import_home, name="import_home"),
    path("import/upload/", views.import_upload, name="import_upload"),
    path("import/pending/", views.import_pending, name="import_pending"),
    path("import/recent/", views.import_recent, name="import_recent"),
]
