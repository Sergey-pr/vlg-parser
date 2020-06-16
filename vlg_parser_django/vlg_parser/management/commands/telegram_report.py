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

        price_message = self.get_price_message(stat)
        price_per_sq_change_message = self.get_price_per_sq_change_message(stat)

        message = f"""На {datetime.now().astimezone(pytz.timezone('Europe/Volgograd')).strftime("%d/%m/%Y, %H:%M")}:

{price_message}
Средняя цена за м²: {self.format_price(stat.price_per_sq)}
{price_per_sq_change_message}

Ссылка на таблицу: <a href="http://vlg-offers.ru">vlg-offers.ru</a>"""

        if stat.interesting_offers.count():
            message += self.get_interesting_offers(stat)

        if stat.avito_new.count():
            message += self.get_avito_new(stat)

        if stat.cian_new.count():
            message += self.get_cian_new(stat)

        changes = self.get_changes()

        if changes:
            message += '\n\nИзменения цен:'
            message += changes

        request = Request(proxy_url=settings.TELEGRAM_PROXY)
        bot = telegram.Bot(token=settings.TELEGRAM_TOKEN, request=request)

        if len(message) < 4096:
            bot.send_message(chat_id=settings.TELEGRAM_CHAT_ID, text=message, parse_mode='HTML')
        else:
            n = 4096
            messages = [message[i:i+n] for i in range(0, len(message), n)]
            for message in messages:
                bot.send_message(chat_id=settings.TELEGRAM_CHAT_ID, text=message, parse_mode='HTML')

    def get_cian_new(self, stat):
        message = '\n\nНовые объявления на циан:\n'
        for offer in stat.cian_new.all().order_by('cian_price'):
            price = self.format_price(offer.cian_price)
            message += f'\n{price}, {offer.area} м²\n{offer.cian_url}'
        return message

    def get_avito_new(self, stat):
        message = '\n\nНовые объявления на авито:\n'
        for offer in stat.avito_new.all().order_by('avito_price'):
            price = self.format_price(offer.avito_price)
            message += f'\n{price}, {offer.area} м²\n{offer.avito_url}'
        return message

    def get_interesting_offers(self, stat):
        message = '\n\nИнтересные предложения:\n(40м² за 1 500 000)\n'
        for offer in stat.interesting_offers.all():
            if offer.avito_price:
                price = self.format_price(offer.avito_price)
                message += f'\n{price}, {offer.area} м²\n{offer.avito_url}'
            else:
                price = self.format_price(offer.cian_price)
                message += f'\n{price}, {offer.area} м²\n{offer.cian_url}'
        return message

    @staticmethod
    def get_price_per_sq_change_message(stat):
        price_per_sq_change_message = 'Средняя цена за м² не изменилась'
        if stat.price_per_sq_change:
            if float(stat.price_per_sq_change) < 0:
                price_per_sq_change_message = f'Средняя цена за м² упала на: {stat.price_per_sq_change}%'
            elif float(stat.price_per_sq_change) > 0:
                price_per_sq_change_message = f'Средняя цена за м² поднялась на: {stat.price_per_sq_change}%'
        return price_per_sq_change_message

    @staticmethod
    def get_price_message(stat):
        price_message = 'Цены на квартиры не изменились'
        if stat.price_change:
            if float(stat.price_change) < 0:
                price_message = f'Цены на квартиры упали на {stat.price_change}%'
            elif float(stat.price_change) > 0:
                price_message = f'Цены на квартиры поднялись на {stat.price_change}%'
        return price_message

    def get_changes(self):
        last_day = datetime.today() - timedelta(days=1)
        offers = Offer.objects.filter(price_change_date__gte=last_day)

        if not offers:
            return

        message = ''
        for offer in offers:
            if offer.avito_old_prices:
                message += self.get_avito_changes(offer)

            elif offer.cian_old_prices:
                message += self.get_cian_changes(offer)

        return message

    def get_avito_changes(self, offer):
        message = ''
        old_price = offer.avito_old_prices[-1]
        price = offer.avito_price
        if price == old_price:
            return ''
        if price > old_price:
            symbol = '❌'
        else:
            symbol = '✅'
        message += f'\n\n{self.format_price(old_price)} -> {self.format_price(price)} {symbol}'
        message += f'\nПлощадь: {offer.area} м²'
        message += f'\n{offer.avito_url}'
        return message

    def get_cian_changes(self, offer):
        message = ''
        old_price = offer.cian_old_prices[-1]
        price = offer.cian_price
        if price == old_price:
            return ''
        if price > old_price:
            symbol = '❌'
        else:
            symbol = '✅'
        message += f'\n\n{self.format_price(old_price)} -> {self.format_price(price)} {symbol}'
        message += f'\nПлощадь: {offer.area} м²'
        message += f'\n{offer.cian_url}'
        return message

    @staticmethod
    def format_price(price):
        price = "{0:,}".format(price).replace(',', ' ').replace('.0', '') + ' ₽'
        return price
