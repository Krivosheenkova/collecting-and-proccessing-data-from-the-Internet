import scrapy
from books_scraper.items import BooksScraperItem


class Book24ruSpider(scrapy.Spider):
    name = 'book24ru'
    allowed_domains = ['book24.ru']
    start_urls = ['https://book24.ru/novie-knigi/?saleleader=1/']

    def parse(self, response):
        books_links = response.xpath('//a[@class="book-preview__title-link"]//@href').extract()

        for link in books_links:
            yield response.follow(link, callback=self.parse_books)

        new_page = response.xpath('''//a[contains (@class, "catalog-pagination__item _text")]
                                    [last()]/@href''').get()
        if new_page:
            yield response.follow(new_page, callback=self.parse)
        pass

    def parse_books(self, response):
        title = response.xpath("//span[@class='breadcrumbs__link'][@title]/text()").get()
        link = response.url
        author = response.xpath("//a[@itemprop='author']/text()").get()
        price = response.xpath('//div[@class="item-actions__price-old"]/text()').get()
        if price:
            price_new = response.xpath('//div[@class="item-actions__price"]/b[position()=1]/text()').get()
        else:
            price = response.xpath('//div[@class="item-actions__price"]/b[position()=1]/text()').get()
            price_new = None
        # rate = response.xpath("//div[@class='rating__rate-value _bold']/text()").get()
        rate = response.xpath("//div[contains (@class, 'rating__value-box')]/span/text()").get()

        yield BooksScraperItem(title=title, link=link,
                               author=author, rate=rate,
                               price=price, price_new=price_new)