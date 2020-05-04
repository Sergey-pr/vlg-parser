import scrapy


GET_TEXT_ATOM = './/text()'
INFO_BLOCK_KEYS = [
    'area',
    'living_area',
    'kitchen_area',
    'floor',
    'built_in'
]


class CianSpider(scrapy.Spider):

    name = "cian_ru"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.url = 'https://volgograd.cian.ru/cat.php?' \
                   'deal_type=sale&district%5B0%5D=280&district%5B1%5D=281&district%5B2%5D=282&engine_version=2&' \
                   'is_by_homeowner=1&object_type%5B0%5D=1&offer_type=flat&room1=1&room2=1&room9=1'
        self.page = 1

    def start_requests(self):
        yield scrapy.Request(self.url, self.parse)

    def parse(self, response):
        for card in response.xpath('//div[@data-name="Offers"]/div'):
            if not card.attrib.get('class') or 'card' not in card.attrib.get('class'):
                continue

            card_link_a = card.xpath('div/div[1]/div/div[2]/div[1]/div[1]/div[1]/div/a')
            card_link = card_link_a.attrib.get('href')

            yield response.follow(card_link, self.parse_card)

        self.page += 1
        if self.page < 10:
            yield response.follow(self.url + f'&p={self.page}', self.parse)

    def parse_card(self, response):
        yield {
            'address': response.xpath('//div[@data-name="Geo"]/span').attrib.get('content'),
            'building_info': self.get_building_info(response),
            'price': response.xpath('//span[@itemprop="price"]').xpath(GET_TEXT_ATOM).get(),
            'name': response.xpath('//h1[@data-name="OfferTitle"]').xpath(GET_TEXT_ATOM).get(),
            'url': response.request.url,
            'cian_id': response.request.url.split('/')[-2],
            **self.get_bonus_info_block(response),
            **self.get_info_block(response)
        }

    @staticmethod
    def get_building_info(response):
        bonus_addresses = []
        if response.xpath('//div[@data-name="Parent"]'):
            for span in response.xpath('//div[@data-name="Parent"]/span'):
                bonus_addresses.append(span.xpath(GET_TEXT_ATOM).get())
        return ''.join([x for x in bonus_addresses if x])

    def get_info_block(self, response) -> dict:
        info_block_values = {}
        for info_block in response.xpath('//div[@data-name="Description"]/div/div/div'):
            info_block_dict = self.get_info_block_dict(info_block)
            if info_block_dict:
                info_block_values.update(info_block_dict)
        return info_block_values

    @staticmethod
    def get_info_block_dict(info_block):
        key, value = None, None
        for info in info_block.xpath('div'):
            if '--info-value--' in info.attrib.get('class'):
                value = info.xpath(GET_TEXT_ATOM).get()
            if '--info-title--' in info.attrib.get('class'):
                key = info.xpath(GET_TEXT_ATOM).get()
        if key and value:
            return {key: value}
        return {}

    def get_bonus_info_block(self, response) -> dict:
        bonus_info_block_values = {}
        for item in response.xpath('//article[@data-name="AdditionalFeaturesGroup"]/ul/li'):
            span_dict = self.get_key_value(item, 'span')
            if span_dict:
                bonus_info_block_values.update(span_dict)

        for item in response.xpath('//article[@data-name="BtiHouseData"]/div[1]/div/div'):
            div_dict = self.get_key_value(item, 'div')
            if div_dict:
                bonus_info_block_values.update(div_dict)

        return bonus_info_block_values

    @staticmethod
    def get_key_value(obj, type_of_element):
        key, value = None, None
        for sub_obj in obj.xpath(type_of_element):
            if '--name--' in sub_obj.attrib.get('class'):
                key = sub_obj.xpath(GET_TEXT_ATOM).get()
            if '--value--' in sub_obj.attrib.get('class'):
                value = sub_obj.xpath(GET_TEXT_ATOM).get()
        if key and value:
            return {key: value}
        return {}
