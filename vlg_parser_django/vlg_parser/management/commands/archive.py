import datetime

from django.core.management import BaseCommand

from vlg_parser.models import Offer


class Command(BaseCommand):
    def __init__(self):
        super(Command, self).__init__()

    def handle(self, *args, **options):
        now = datetime.datetime.now()
        dt = now - datetime.timedelta(weeks=1)
        offers = Offer.objects.filter(modified__lte=dt)
        offers.update(archived=True)
