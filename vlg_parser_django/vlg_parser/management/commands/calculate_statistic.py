from django.core.management import BaseCommand

from vlg_parser.models import Offer, Statistic


class Command(BaseCommand):
    def __init__(self):
        super(Command, self).__init__()

    def handle(self, *args, **options):
        price_per_sq = self.get_price_per_sq()
        price = self.get_price()
        create_args = {
            'price_per_sq': price_per_sq,
            'interesting_offers': self.get_interesting_offers(),
            'price': price
        }

        if Statistic.objects.count():
            last_statistic = Statistic.objects.latest('created')
            if last_statistic:
                price_per_sq_change = self.get_price_per_sq_change(last_statistic, price_per_sq)
                price_change = self.get_price_change(last_statistic, price)
                create_args.update({
                    'price_per_sq_change': price_per_sq_change,
                    'price_change': price_change
                })

        Statistic.objects.create(**create_args)

    @staticmethod
    def get_price():
        price_list = []
        offers = Offer.objects.filter(price__isnull=False)
        for offer in offers:
            price_list.append(offer.price)
        price = sum(price_list) / len(price_list)
        return round(price, 2)

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
    def get_price_change(last_statistic, price) -> float:
        price_change = 100 - ((round(last_statistic.price, 2) / round(price, 2)) * 100.0)
        return round(price_change, 2)

    @staticmethod
    def get_price_per_sq_change(last_statistic, price_per_sq):
        old_price_per_sq = last_statistic.price_per_sq
        price_per_sq_change = 100 - ((round(old_price_per_sq, 2) / round(price_per_sq, 2)) * 100.0)
        return round(price_per_sq_change, 2)

    @staticmethod
    def get_interesting_offers():
        offers = Offer.objects.filter(price__lte=1200000, area__gte=40)
        urls = [x.url for x in offers]
        return urls
