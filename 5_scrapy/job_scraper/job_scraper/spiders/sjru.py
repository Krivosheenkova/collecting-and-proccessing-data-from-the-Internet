import scrapy
from scrapy.http import HtmlResponse
from job_scraper.items import JobScraperItem


class SjruSpider(scrapy.Spider):
    name = 'sjru'
    allowed_domains = ['superjob.ru']
    start_urls = ['https://www.superjob.ru/vacancy/search/?keywords=python']

    def parse(self, response):
        vacancy_links = response.css('''div.f-test-vacancy-item 
        a[class*=f-test-link][href^="/vakansii"]::attr(href)''').extract()

        for link in vacancy_links:
            yield response.follow(link, callback=self.parse_vacancies)

        next_page = response.xpath('''//a[contains (@class, 'f-test-button-dalshe')]//@href''').extract()

        if next_page:
            yield response.follow(next_page[0], callback=self.parse)
        print('')
        pass

    def parse_vacancies(self, response):
        title = response.css('h1 ::text').get()
        company = response.xpath('//div[@class="_3zucV undefined _3SGgo"][1]//text()').get()
        salary = response.xpath('//span[@class="_1OuF_ ZON4b"][1]//text()').getall()
        link = response.url

        yield JobScraperItem(title=title,
                             company=company,
                             salary=salary,
                             link=link)
