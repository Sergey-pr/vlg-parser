import json
import os

from django.core.management import BaseCommand

from vlg_parser.models import Offer


MAPPING_TO_INT = {
    'Общая площадь': 'area',
    'Жилая площадь': 'living_area',
    'Площадь кухни': 'kitchen_area',
    'price': 'price'
}

MAPPING = {
    'avito_id': 'avito_id',
    'Тип дома': 'house_type',
    'address': 'address',
    'url': 'url',
    'name': 'name',
    'Количество комнат': 'rooms',
    'Год постройки': 'built_in',
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
            avito_id, clean_data = self.parse_data(offer)

            offer_obj = Offer.objects.filter(avito_id=avito_id).first()
            if offer_obj:
                old_price = offer_obj.raw_price
                if old_price != clean_data.get('raw_price'):
                    old_prices = offer_obj.old_prices
                    if not old_prices:
                        old_prices = []
                    old_prices.append(offer_obj.raw_price)
                    offer_obj.old_prices = old_prices
                    offer_obj.save()

            obj, created = Offer.objects.update_or_create(
                avito_id=avito_id,
                defaults=clean_data,
            )
        os.rename(path, path + '.parsed')

    @staticmethod
    def parse_data(data):
        clean_data = {}
        avito_id = None
        floors = None
        current_floor = None
        for key, value in data.items():
            if key == 'avito_id':
                avito_id = value
                continue
            if key == 'Этажей в доме':
                floors = value
            if key == 'Этаж':
                current_floor = value
            if key in MAPPING:
                clean_data.update({MAPPING.get(key): value})
            if key in MAPPING_TO_INT:
                for symbol in ['₽', ' ', '\xa0', 'м²']:
                    value = value.replace(symbol, '')
                value = float(value)
                clean_data.update({MAPPING_TO_INT.get(key): value})
        if current_floor and floors:
            clean_data.update({'floor': f'{current_floor} из {floors}'})
        return avito_id, clean_data
