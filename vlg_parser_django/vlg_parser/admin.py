from django.contrib import admin
from django.utils.html import format_html

from vlg_parser.models import Offer


class OfferAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'price',
        'address',
        'show_url',
        'area',
        'floor',
        'kitchen_area',
        'built_in',
        'house_type',
        'ceiling_height',
        'water_closet',
        'balcony',
        'renovation',
        'view_from_windows',
        'living_area',
        'rooms',
        'plan',
        'type',
        'building_info',
        'cian_id',
        'avito_id',
        'old_prices',
        'modified'
    ]

    def show_url(self, obj):
        return format_html("<a href='{url}'>{url}</a>", url=obj.url)

    show_url.short_description = "URL"


admin.site.register(Offer, OfferAdmin)
