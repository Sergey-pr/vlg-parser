from django.db import models
from django.contrib.postgres.fields import ArrayField
from django_extensions.db.fields import ModificationDateTimeField
from django_extensions.db.models import TimeStampedModel


class Offer(TimeStampedModel):
    modified = ModificationDateTimeField('Обновлено')

    class Meta:
        db_table = 'offer'

    cian_id = models.CharField(max_length=512, blank=True, null=True)
    cian_url = models.URLField(max_length=512, blank=True, null=True)
    cian_price = models.FloatField("Цена Cian", null=True, blank=True)
    avito_id = models.CharField(max_length=512, blank=True, null=True)
    avito_url = models.URLField(max_length=512, blank=True, null=True)
    avito_price = models.FloatField("Цена Avito", null=True, blank=True)
    price = models.FloatField("Цена", null=True, blank=True)
    address = models.CharField("Адрес", max_length=512, blank=True, null=True)
    area = models.FloatField("Площадь", blank=True, null=True)
    floor = models.CharField("Этаж", max_length=512, blank=True, null=True)
    type = models.CharField(max_length=512, blank=True, null=True)
    ceiling_height = models.CharField(max_length=512, blank=True, null=True)
    water_closet = models.CharField(max_length=512, blank=True, null=True)
    balcony = models.CharField(max_length=512, blank=True, null=True)
    renovation = models.CharField(max_length=512, blank=True, null=True)
    view_from_windows = models.CharField(max_length=512, blank=True, null=True)
    kitchen_area = models.FloatField("Площадь кухни", blank=True, null=True)
    living_area = models.FloatField(blank=True, null=True)
    built_in = models.CharField("Год", max_length=512, blank=True, null=True)
    plan = models.CharField(max_length=512, blank=True, null=True)
    building_info = models.CharField(max_length=512, blank=True, null=True)
    name = models.CharField("Название", max_length=512, blank=True, null=True, default='Квартира')
    cian_old_prices = ArrayField(
        models.IntegerField(null=True, blank=True),
        verbose_name="Старая цена Cian",
        null=True,
        blank=True
    )
    avito_old_prices = ArrayField(
        models.IntegerField(null=True, blank=True),
        verbose_name="Старая цена Avito",
        null=True,
        blank=True
    )
    house_type = models.CharField(max_length=512, blank=True, null=True)
    rooms = models.CharField(max_length=512, blank=True, null=True)

    def __str__(self):
        if self.cian_id or self.avito_id:
            return self.cian_id if self.cian_id else self.avito_id
        else:
            return ''


class Statistic(TimeStampedModel):
    modified = ModificationDateTimeField('Обновлено')

    class Meta:
        db_table = 'statistic'

    price = models.FloatField("Цена за м²", null=True, blank=True)
    price_change = models.FloatField("Изменение цены", blank=True, null=True)
    price_per_sq_change = models.FloatField("Изменение цены за м²", blank=True, null=True)
    price_per_sq = models.FloatField("Цена за м²", null=True, blank=True)
    interesting_offers = ArrayField(
        models.CharField(max_length=512, null=True, blank=True),
        verbose_name="Интересные предложения",
        null=True,
        blank=True
    )
    avito_new = models.ManyToManyField(Offer, related_name='avito_new')
    cian_new = models.ManyToManyField(Offer, related_name='cian_new')

