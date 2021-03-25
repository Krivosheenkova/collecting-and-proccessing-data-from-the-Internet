import scrapy
from media_scraping.items import MediaScrapingItem
from scrapy.loader import ItemLoader


class LeroymerlinruSpider(scrapy.Spider):
    name = 'leroymerlinru'
    allowed_domains = ['leroymerlin.ru']
    base_url = 'https://leroymerlin.ru'

    def __init__(self, search):
        super().__init__()
        self.start_urls = [f'https://leroymerlin.ru/search/?q={search}']
        self.driver = webdriver.Chrome()

    def parse(self, response):
        links = response.xpath('//product-card/@data-product-url').extract()
        for link in links:
            yield response.follow(link, callback=self.parse_product)

        next_page_part = response.xpath('//a[contains (@class, "paginator-button next-paginator-button")]/@href').get()
        if next_page_part:
            next_page = self.base_url + next_page_part
            yield scrapy.Request(next_page, callback=self.parse)

    def parse_product(self, response):
        loader = ItemLoader(item=MediaScrapingItem(), response=response)
        loader.add_xpath('images', "//img[@slot='thumbs']/@src")
        loader.add_xpath('name', "//h1[@itemprop='name']/text()")
        loader.add_xpath('price', "//meta[@itemprop='price']/@content")
        loader.add_value('link', response.url)
        loader.add_xpath('params', """//div[@class='def-list__group']/dt/text() |
                                      //div[@class='def-list__group']/dd/text()""")
        yield loader.load_item()
