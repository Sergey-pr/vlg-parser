from django.shortcuts import render

from django_tables2 import RequestConfig


from .models import Offer
from .tables import (
    OfferTable,
)


def index(request):
    table = OfferTable(Offer.objects.all(), order_by="price")
    RequestConfig(request, paginate={"per_page": 20}).configure(table)

    return render(
        request,
        "index.html",
        {
            "table": table,
        },
    )
