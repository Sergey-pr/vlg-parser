import json
import os

from datetime import datetime

from django.core.management import BaseCommand

from vlg_parser.models import Offer

MAPPING_TO_INT = {
    'Общая': 'area',
    'Жилая': 'living_area',
    'Кухня': 'kitchen_area',
    'price': 'price'
}
MAPPING = {
    'cian_id': 'cian_id',
    'Планировка': 'plan',
    'address': 'address',
    'url': 'url',
    'Тип жилья': 'type',
    'Высота потолков': 'ceiling_height',
    'Санузел': 'water_closet',
    'Балкон/лоджия': 'balcony',
    'Ремонт': 'renovation',
    'Вид из окон': 'view_from_windows',
    'Этаж': 'floor',
    'Построен': 'built_in',
    'building_info': 'building_info',
    'name': 'name'
}


class Command(BaseCommand):
    def __init__(self):
        super(Command, self).__init__()

    def add_arguments(self, parser):
        parser.add_argument('--path_to_file', type=str, required=True)

    def handle(self, *args, **options):
        path = options.get('path_to_file')
        with open(path) as json_file:
            data = json.load(json_file)

        for offer in data:
            cian_id, clean_data = self.parse_data(offer)

            if not cian_id or clean_data.get('name'):
                continue

            offer_obj = Offer.objects.filter(cian_id=cian_id).first()
            if offer_obj:
                old_price = offer_obj.price
                if old_price != clean_data.get('price'):
                    old_prices = offer_obj.old_prices
                    if not old_prices:
                        old_prices = []
                    old_prices.append(offer_obj.price)
                    offer_obj.old_prices = old_prices
                    offer_obj.save()

            obj, created = Offer.objects.update_or_create(
                cian_id=cian_id,
                defaults=clean_data,
            )
        os.rename(path, f'{path}.parsed_{datetime.now().timestamp()}')

    @staticmethod
    def parse_data(data):
        clean_data = {}
        cian_id = None
        for key, value in data.items():
            if not value:
                continue
            if key == 'cian_id':
                cian_id = value
                continue
            if key in MAPPING:
                clean_data.update({MAPPING.get(key): value})
            if key in MAPPING_TO_INT:
                for symbol in ['₽', ' ', '\xa0', 'м²']:
                    value = value.replace(symbol, '')
                value = value.replace(',', '.')
                value = float(value)
                clean_data.update({MAPPING_TO_INT.get(key): value})
        return cian_id, clean_data
