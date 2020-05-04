import django_tables2 as tables
from django.utils.html import format_html

from .models import Offer


class OfferTable(tables.Table):
    price = tables.Column(attrs={"th": {"style": "width: 100px"}})
    name = tables.Column()
    area = tables.Column()
    kitchen_area = tables.Column()
    floor = tables.Column(attrs={"th": {"style": "width: 70px"}})
    old_prices = tables.Column(attrs={"th": {"style": "width: 100px"}})

    def render_price(self, value, record):
        return "{0:,}".format(value).replace(',', ' ').replace('.0', '') + ' ₽'

    def render_old_prices(self, value, record):
        if value and value != [None]:
            return "{0:,}".format(value[-1]).replace(',', ' ').replace('.0', '') + ' ₽'
        else:
            return '—'

    def render_name(self, value, record):
        return format_html("<a href={}>{}</b>", record.url, value)

    def render_area(self, value, record):
        return str(value).replace('.', ',') + ' м²'

    def render_kitchen_area(self, value, record):
        return str(value).replace('.', ',') + ' м²'

    class Meta:
        model = Offer
        template_name = "django_tables2/bootstrap.html"
        fields = (
            'name',
            'price',
            'address',
            'area',
            'floor',
            'kitchen_area',
            'built_in',
            'old_prices',
            'modified'
        )
