from django.urls import path

from vlg_parser.views import (
    index,
)

urlpatterns = [
    path("", index),
]
