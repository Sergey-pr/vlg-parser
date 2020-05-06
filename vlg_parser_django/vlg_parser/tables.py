import django_tables2 as tables
from django.utils.html import format_html

from .models import Offer


CURRENCY_FORMAT = "{0:,}"


class OfferTable(tables.Table):
    price = tables.Column(attrs={"th": {"style": "width: 100px"}})
    name = tables.Column()
    area = tables.Column()
    kitchen_area = tables.Column()
    floor = tables.Column(attrs={"th": {"style": "width: 70px"}})
    old_prices = tables.Column(attrs={"th": {"style": "width: 100px"}}, verbose_name='Старая цена', orderable=False)

    def render_price(self, value, record):
        avito_price = record.avito_price
        cian_price = record.cian_price
        message = ''
        if avito_price:
            avito = CURRENCY_FORMAT.format(avito_price).replace('.0', '') + ' ₽'
            message += f'Avito:<br>{avito}<br>'
        if cian_price:
            cian = CURRENCY_FORMAT.format(cian_price).replace('.0', '') + ' ₽'
            message += f'Cian:<br>{cian}'
        return format_html(message)

    def render_old_prices(self, value, record):
        if value and value != [None]:
            avito_price = record.avito_old_prices[-1]
            cian_price = record.cian_old_prices[-1]
            message = ''
            if avito_price:
                avito = CURRENCY_FORMAT.format(avito_price).replace('.0', '') + ' ₽'
                message += f'Avito:<br>{avito}<br>'
            if cian_price:
                cian = CURRENCY_FORMAT.format(cian_price).replace('.0', '') + ' ₽'
                message += f'Cian:<br>{cian}'
            return format_html(message)
        else:
            return '—'

    def render_name(self, value, record):
        message = value + '<br>'
        if record.avito_url:
            message += format_html("<a href={}>Avito </a>", record.avito_url)
        if record.cian_url:
            message += format_html("<a href={}>Cian </a>", record.cian_url)
        return format_html(message)

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
            'modified'
        )
