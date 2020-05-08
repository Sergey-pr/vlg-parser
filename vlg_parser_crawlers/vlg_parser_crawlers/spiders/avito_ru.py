import scrapy


GET_TEXT_ATOM = './/text()'


class AvitoSpider(scrapy.Spider):
    name = "avito_ru"
    download_delay = 10

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.url = 'https://www.avito.ru/volgograd/kvartiry/prodam-ASgBAgICAUSSA8YQ' \
                   '?cd=1&pmax=2000000&district=2-3-9&f=ASgBAQECAUSSA8YQAUDKCDSCWYBZ' \
                   '_lgCReIHF3siZnJvbSI6NTE4OCwidG8iOm51bGx9hAkVeyJmcm9tIjoyNSwidG8iOm51bGx9'
        self.page = 1

    def start_requests(self):
        yield scrapy.Request(self.url, self.parse)

    def parse(self, response):
        for card_link in response.xpath('//a[@class="snippet-link"]'):
            link = card_link.attrib.get('href')

            yield response.follow(link, self.parse_card)

        self.page += 1
        if self.page < 10:
            yield response.follow(self.url + f'&p={self.page}', self.parse)

    def parse_card(self, response):
        address = str(response.xpath('//span[@class="item-address__string"]')
                      .xpath(GET_TEXT_ATOM).get()).replace('\n', '').strip()
        yield {
            'name': response.xpath('//span[@class="title-info-title-text"]').xpath(GET_TEXT_ATOM).get(),
            'address': address,
            'price': response.xpath('//span[@class="js-item-price"]').xpath(GET_TEXT_ATOM).get(),
            'url': response.request.url,
            'avito_id': response.request.url.split('_')[-1],
            **self.get_info_block(response)
        }

    @staticmethod
    def get_info_block(response) -> dict:
        info = {}
        for item in response.xpath('//li[@class="item-params-list-item"]'):
            item_list = item.xpath(GET_TEXT_ATOM).getall()
            info.update({
                item_list[1].replace(': ', ''): str(item_list[2]).strip()
            })
        return info

    @staticmethod
    def get_key_value(obj):
        key, value = None, None
        if '--name--' in obj.attrib.get('class'):
            key = obj.xpath(GET_TEXT_ATOM).get()
        if '--value--' in obj.attrib.get('class'):
            value = obj.xpath(GET_TEXT_ATOM).get()
        if key and value:
            return {key: value}
        return None
