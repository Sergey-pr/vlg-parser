import telegram
from telegram.utils.request import Request
from datetime import datetime
import pytz
from django.core.management import BaseCommand

from vlg_parser.models import Statistic


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
Средняя цена за м²: {"{0:,}".format(stat.price_per_sq).replace(',', ' ').replace('.0', '') + ' ₽'}
{price_per_sq_change_message}
"""
        if offers:
            message += '\nИнтересные предложения:\n' + offers

        request = Request(proxy_url='socks5h://85.10.235.14:1080')
        bot = telegram.Bot(token='1110571536:AAGWx4vDfuF7TJSd3W--ylZ1U6Axms9ze0o', request=request)
        bot.send_message(chat_id='-1001127435195', text=message)

