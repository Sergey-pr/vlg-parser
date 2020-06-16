import json
import os

from datetime import datetime
from urllib.parse import quote_plus

import requests
from django.conf import settings
from django.core.management import BaseCommand, CommandError

from vlg_parser.models import Offer, Statistic


MAPPING_TO_INT = {
    'Общая площадь': 'area',
    'Жилая площадь': 'living_area',
    'Площадь кухни': 'kitchen_area',
    'price': 'avito_price'
}

MAPPING = {
    'avito_id': 'avito_id',
    'Тип дома': 'house_type',
    'url': 'avito_url',
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

        obj_list = self.process_offers(data)

        if Statistic.objects.count():
            last_statistic = Statistic.objects.latest('created')
            last_statistic.avito_new.set(obj_list)

        os.rename(path, f'{path}.parsed_{datetime.now().timestamp()}')

    def process_offers(self, data):
        obj_list = []
        for offer in data:
            clean_data = self.parse_data(offer)

            if not clean_data.get('avito_id') or not clean_data.get('name') \
                    or not clean_data.get('address') or not clean_data.get('floor'):
                continue

            clean_data['price'] = clean_data.get('avito_price')

            offer_obj = Offer.objects.filter(avito_id=clean_data.get('avito_id')).first()
            if offer_obj:
                old_price = offer_obj.avito_price
                if old_price != clean_data.get('avito_price'):
                    old_prices = offer_obj.avito_old_prices
                    if not old_prices:
                        old_prices = []
                    old_prices.append(offer_obj.price)
                    offer_obj.avito_old_prices = old_prices
                    offer_obj.price_change_date = datetime.now()
                    offer_obj.save()

            obj, created = Offer.objects.update_or_create(
                address=clean_data.get('address'),
                area=clean_data.get('area'),
                floor=clean_data.get('floor'),
                defaults=clean_data,
            )
            if created:
                obj_list.append(obj)
        return obj_list

    def parse_data(self, data):
        clean_data = {}
        floors, current_floor = None, None
        for key, value in data.items():
            if not value:
                continue
            if key == 'Этажей в доме':
                floors = value
            if key == 'Этаж':
                current_floor = value
            if key == 'address':
                address = self.get_address(value)
                clean_data.update({'address': address})
            if key in MAPPING:
                clean_data.update({MAPPING.get(key): value})
            if key in MAPPING_TO_INT:
                value = self.clean_value(value)
                value = float(value)
                clean_data.update({MAPPING_TO_INT.get(key): value})
        if current_floor and floors:
            clean_data.update({'floor': f'{current_floor} из {floors}'})
        return clean_data

    @staticmethod
    def clean_value(value):
        for symbol in ['₽', ' ', '\xa0', 'м²']:
            value = value.replace(symbol, '')
        value = value.replace(',', '.')
        return value

    @staticmethod
    def get_address(value):
        api_key = settings.YANDEX_TOKEN
        value = quote_plus(value)
        endpoint = f'https://geocode-maps.yandex.ru/1.x/?apikey={api_key}&format=json&geocode={value}'
        response = requests.get(endpoint)
        if not response.ok:
            raise CommandError('Yandex api error')
        response_dict = response.json()
        address_list = response_dict['response']['GeoObjectCollection'].get('featureMember')
        if address_list:
            address = address_list[0]['GeoObject']['metaDataProperty']['GeocoderMetaData']['text']
            return address
        return None
