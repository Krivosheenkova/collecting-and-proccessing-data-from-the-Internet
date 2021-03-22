import scrapy
from books_scraper.items import BooksScraperItem


class LabirintruSpider(scrapy.Spider):
    name = 'labirintru'
    allowed_domains = ['labirint.ru']
    start_urls = ['https://www.labirint.ru/best/']

    def parse(self, response):
        books_links = response.xpath("""//a[@class='cover'][@title]/@href |
        //span[@class="b-productblock-e-cover"]//a[@class='b-product-block-link']//@href""").extract()

        new_page = response.xpath("""//div[@class='pagination-next']//@href""").get()

        for link in books_links:
            yield response.follow(link, callback=self.parse_books)

        if new_page:
            new_page = 'https://www.labirint.ru/best/' + new_page
            yield response.follow(new_page, callback=self.parse)
        pass

    def parse_books(self, response):
        link = response.url
        title = response.xpath('//meta[@property="og:title"]/@content').get()
        author = response.xpath("//div[@class='authors']/a/text()").get()
        rate = response.css('#rate ::text').get()
        price = response.xpath("""//span[@class='buying-price-val-number']/text()""").get()
        if not price:
            price = response.xpath("""//span[@class='buying-priceold-val-number']/text()""").get()
            price_new = response.xpath("""//span[@class='buying-pricenew-val-number']/text()""").get()
        else:
            price_new = None
        currency = response.xpath('''//span[@class="buying-pricenew-val-currency"]/text()''').get()
        yield BooksScraperItem(title=title, link=link,
                               author=author, rate=rate,
                               price=price, price_new=price_new,
                               currency=currency)
