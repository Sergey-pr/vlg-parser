from django.core.management import BaseCommand
from django.db.models import Q

from vlg_parser.models import Offer, Statistic


class Command(BaseCommand):
    def __init__(self):
        super(Command, self).__init__()

    def handle(self, *args, **options):
        price_per_sq = self.get_price_per_sq()
        price = self.get_price()
        price_change = self.get_price_change()
        create_args = {
            'price_per_sq': price_per_sq,
            'interesting_offers': self.get_interesting_offers(),
            'price': price,
            'price_change': price_change
        }

        new_avito_offers = None
        new_cian_offers = None
        if Statistic.objects.count():
            last_statistic = Statistic.objects.latest('created')
            if last_statistic:
                new_avito_offers = list(last_statistic.avito_new.all())
                new_cian_offers = list(last_statistic.cian_new.all())
                price_per_sq_change = self.get_price_per_sq_change(last_statistic, price_per_sq)
                create_args.update({
                    'price_per_sq_change': price_per_sq_change,
                })

        stat_obj = Statistic.objects.create(**create_args)
        if new_avito_offers:
            stat_obj.avito_new.set(new_avito_offers)
        if new_cian_offers:
            stat_obj.cian_new.set(new_cian_offers)

    @staticmethod
    def get_price():
        price_list = []
        avito_offers = Offer.objects.filter(avito_price__isnull=False)
        for offer in avito_offers:
            price_list.append(offer.avito_price)
        avito_offers = Offer.objects.filter(cian_price__isnull=False)
        for offer in avito_offers:
            price_list.append(offer.cian_price)
        price = sum(price_list) / len(price_list)
        return round(price, 2)

    @staticmethod
    def get_price_per_sq():
        prices_per_sq_list = []
        avito_offers_with_sq = Offer.objects.filter(area__isnull=False, avito_price__isnull=False)
        for offer in avito_offers_with_sq:
            offer_price_per_sq = offer.avito_price / offer.area
            prices_per_sq_list.append(offer_price_per_sq)
        cian_offers_with_sq = Offer.objects.filter(area__isnull=False, cian_price__isnull=False)
        for offer in cian_offers_with_sq:
            offer_price_per_sq = offer.cian_price / offer.area
            prices_per_sq_list.append(offer_price_per_sq)
        price_per_sq = sum(prices_per_sq_list) / len(prices_per_sq_list)
        return round(price_per_sq, 2)

    @staticmethod
    def get_price_change() -> float:
        old_prices = []
        new_prices = []
        offers = Offer.objects.filter(Q(avito_old_prices__isnull=False) | Q(cian_old_prices__isnull=False))
        for offer in offers:
            if offer.avito_old_prices:
                old_prices.append(offer.avito_old_prices[-1])
                new_prices.append(offer.avito_price)
            if offer.cian_old_prices:
                old_prices.append(offer.cian_old_prices[-1])
                new_prices.append(offer.cian_price)
        if not old_prices or not new_prices:
            return 0.0
        old_price = round(sum(old_prices) / len(old_prices), 2)
        new_price = round(sum(new_prices) / len(new_prices), 2)
        price_change = 100 - ((round(old_price, 2) / round(new_price, 2)) * 100.0)
        return round(price_change, 2)

    @staticmethod
    def get_price_per_sq_change(last_statistic, price_per_sq):
        old_price_per_sq = last_statistic.price_per_sq
        price_per_sq_change = 100 - ((round(old_price_per_sq, 2) / round(price_per_sq, 2)) * 100.0)
        return round(price_per_sq_change, 2)

    @staticmethod
    def get_interesting_offers():
        offers = Offer.objects.filter(Q(cian_price__lte=1500000) | Q(avito_price__lte=1500000), area__gte=40)
        urls = [x.url for x in offers]
        return urls
