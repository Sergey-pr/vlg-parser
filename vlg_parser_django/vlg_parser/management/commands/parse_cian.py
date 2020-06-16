import json
import os
from urllib.parse import quote_plus

import requests

from datetime import datetime

from django.conf import settings
from django.core.management import BaseCommand, CommandError

from vlg_parser.models import Offer, Statistic

MAPPING_TO_INT = {
    'Общая': 'area',
    'Жилая': 'living_area',
    'Кухня': 'kitchen_area',
    'price': 'cian_price'
}
MAPPING = {
    'cian_id': 'cian_id',
    'Планировка': 'plan',
    'url': 'cian_url',
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

        obj_list = self.process_offers(data)

        if Statistic.objects.count():
            last_statistic = Statistic.objects.latest('created')
            last_statistic.cian_new.set(obj_list)
        os.rename(path, f'{path}.parsed_{datetime.now().timestamp()}')

    def process_offers(self, data):
        obj_list = []
        for offer in data:
            clean_data = self.parse_data(offer)

            if not clean_data.get('cian_id') or not clean_data.get('name') \
                    or not clean_data.get('address') or not clean_data.get('floor'):
                continue

            clean_data['price'] = clean_data.get('cian_price')

            offer_obj = Offer.objects.filter(cian_id=clean_data.get('cian_id')).first()
            if offer_obj:
                old_price = offer_obj.cian_price
                if old_price != clean_data.get('cian_price'):
                    old_prices = offer_obj.cian_old_prices
                    if not old_prices:
                        old_prices = []
                    old_prices.append(offer_obj.price)
                    offer_obj.cian_old_prices = old_prices
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
        for key, value in data.items():
            if not value:
                continue
            if key == 'address':
                address = self.get_address(value)
                clean_data.update({'address': address})
            if key in MAPPING:
                clean_data.update({MAPPING.get(key): value})
            if key in MAPPING_TO_INT:
                for symbol in ['₽', ' ', '\xa0', 'м²']:
                    value = value.replace(symbol, '')
                value = value.replace(',', '.')
                value = float(value)
                clean_data.update({MAPPING_TO_INT.get(key): value})
        return clean_data

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
