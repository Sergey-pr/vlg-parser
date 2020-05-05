from django.core.management import BaseCommand

from vlg_parser.models import Offer, Statistic


class Command(BaseCommand):
    def __init__(self):
        super(Command, self).__init__()

    def handle(self, *args, **options):
        price_per_sq = self.get_price_per_sq()
        create_args = {
            'price_per_sq': price_per_sq,
            'price_change': self.get_price_change(),
            'interesting_offers': self.get_interesting_offers()
        }

        if Statistic.objects.count():
            last_statistic = Statistic.objects.latest('created')
            if last_statistic:
                price_per_sq_change = self.get_price_per_sq_change(last_statistic, price_per_sq)
                create_args.update({'price_per_sq_change': price_per_sq_change})

        Statistic.objects.create(**create_args)

    @staticmethod
    def get_price_per_sq():
        prices_per_sq_list = []
        offers_with_sq = Offer.objects.filter(area__isnull=False, price__isnull=False)
        for offer in offers_with_sq:
            offer_price_per_sq = offer.price / offer.area
            prices_per_sq_list.append(offer_price_per_sq)
        price_per_sq = sum(prices_per_sq_list) / len(prices_per_sq_list)
        return round(price_per_sq, 2)

    @staticmethod
    def get_price_change():
        prices_change_list = []
        offers = Offer.objects.filter(price__isnull=False, old_prices__isnull=False)
        for offer in offers:
            last_price = offer.old_prices[-1]
            current_price = offer.price
            if not last_price or not current_price:
                continue
            price_change = 100 - ((round(last_price, 2) / round(current_price, 2)) * 100.0)
            prices_change_list.append(price_change)
        prices_change = sum(prices_change_list) / len(prices_change_list)
        return round(prices_change, 2)

    @staticmethod
    def get_price_per_sq_change(last_statistic, price_per_sq):
        old_price_per_sq = last_statistic.price_per_sq
        price_per_sq_change = 100 - ((round(old_price_per_sq, 2) / round(price_per_sq, 2)) * 100.0)
        return round(price_per_sq_change, 2)

    @staticmethod
    def get_interesting_offers():
        offers = Offer.objects.filter(price__lte=1200000, area__gte=50)
        urls = [x.url for x in offers]
        return urls
