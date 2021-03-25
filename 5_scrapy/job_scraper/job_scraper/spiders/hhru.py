import scrapy
from scrapy.http import HtmlResponse
from job_scraper.items import JobScraperItem


class HHruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']
    start_urls = ['https://hh.ru/search/vacancy?area=&fromSearchLine=true&'
                  'items_on_page=100&st=searchVacancy&text=python']

    def parse(self, response):
        vacancy_links = response.xpath('''//div[contains(@class, "vacancy-serp-item")]
        //a[contains(@class, "HH-LinkModifier")]/@href''').extract()

        for link in vacancy_links:
            yield response.follow(link, callback=self.parse_vacancies)

        next_page = response.xpath('''//a[contains(@class, "-Pager-Controls-Next")]/@href''').extract()
        if next_page:
            yield response.follow('https://hh.ru' + next_page[0], callback=self.parse)
        pass

    def parse_vacancies(self, response):
        title = response.xpath('//h1//text()').get()
        company = response.xpath("//a[contains (@class, 'vacancy-company-name')]//span/text()").getall()
        salary = response.xpath("//p[contains (@class, 'vacancy-salary')]//span/text()").getall()
        link = response.url

        yield JobScraperItem(title=title,
                             company=company,
                             salary=salary,
                             link=link)
