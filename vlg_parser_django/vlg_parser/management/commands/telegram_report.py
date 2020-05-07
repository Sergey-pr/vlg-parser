import textwrap

import telegram
from django.conf import settings
from django.db.models import Q
from telegram.utils.request import Request
from datetime import datetime, timedelta
import pytz
from django.core.management import BaseCommand

from vlg_parser.models import Statistic, Offer


class Command(BaseCommand):
    def __init__(self):
        super(Command, self).__init__()

    def handle(self, *args, **options):
        stat = Statistic.objects.latest('created')

        offers = '\n'.join(stat.interesting_offers)

        if float(stat.price_change) <= 0:
            price_message = f'Цены на квартиры упали на {stat.price_change}%'
        else:
            price_message = f'Цены на квартиры поднялись на {stat.price_change}%'

        if float(stat.price_per_sq_change) <= 0:
            price_per_sq_change_message = f'Средняя цена за м² упала на: {stat.price_per_sq_change}%'
        else:
            price_per_sq_change_message = f'Средняя цена за м² поднялась на: {stat.price_per_sq_change}%'

        message = f"""На {datetime.now().astimezone(pytz.timezone('Europe/Volgograd')).strftime("%d/%m/%Y, %H:%M")}:

{price_message}
Средняя цена за м²: {self.format_price(stat.price_per_sq)}
{price_per_sq_change_message}
"""
        if offers:
            message += '\nИнтересные предложения (40м² за 1 200 000):\n' + offers

        if stat.avito_new.count():
            message += '\n\nНовые объявления на авито:\n'
            for offer in stat.avito_new.all().order_by('avito_price'):
                price = self.format_price(offer.avito_price)
                message += f'\n{price}, {offer.area} м²\n{offer.avito_url}'
        if stat.cian_new.count():
            message += '\n\nНовые объявления на циан:\n'
            for offer in stat.cian_new.all().order_by('cian_price'):
                price = self.format_price(offer.cian_price)
                message += f'\n{price}, {offer.area} м²\n{offer.cian_url}'

        changes = self.get_changes()

        if changes:
            message += '\n\nИзменения цен:\n'
            message += changes

        request = Request(proxy_url=settings.TELEGRAM_PROXY)
        bot = telegram.Bot(token=settings.TELEGRAM_TOKEN, request=request)

        if len(message) < 4096:
            bot.send_message(chat_id=settings.TELEGRAM_CHAT_ID, text=message)
        else:
            n = 4096
            messages = [message[i:i+n] for i in range(0, len(message), n)]
            for message in messages:
                bot.send_message(chat_id=settings.TELEGRAM_CHAT_ID, text=message)

    def get_changes(self):
        last_day = datetime.today() - timedelta(days=1)
        offers = Offer.objects.filter(
            Q(avito_old_prices__isnull=False) | Q(cian_old_prices__isnull=False),
            modified__gte=last_day
        )

        if not offers:
            return

        message = ''
        for offer in offers:
            if offer.avito_old_prices:
                old_price = offer.avito_old_prices[-1]
                price = offer.avito_price
                if price == old_price:
                    continue
                if price > old_price:
                    symbol = ':x:'
                else:
                    symbol = ':white_check_mark:'
                message += f'\n{self.format_price(old_price)} -> {self.format_price(price)} {symbol}'
                message += f'\nПлощадь: {offer.area} м²'
                message += f'\n{offer.avito_url}'

            elif offer.cian_old_prices:
                old_price = offer.cian_old_prices[-1]
                price = offer.cian_price
                if price == old_price:
                    continue
                if price > old_price:
                    symbol = ':x:'
                else:
                    symbol = ':white_check_mark:'
                message += f'\n{self.format_price(old_price)} -> {self.format_price(price)} {symbol}'
                message += f'\nПлощадь: {offer.area} м²'
                message += f'\n{offer.cian_url}'
        return message

    @staticmethod
    def format_price(price):
        price = "{0:,}".format(price).replace(',', ' ').replace('.0', '') + ' ₽'
        return price
