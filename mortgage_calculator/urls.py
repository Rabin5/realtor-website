# mortgage_calculator/urls.py
from django.urls import path
from . import views

app_name = "mortgage_calculator"

urlpatterns = [
    path("", views.widget, name="widget"),
    path("api/calc/", views.calc_api, name="calc_api"),
]
