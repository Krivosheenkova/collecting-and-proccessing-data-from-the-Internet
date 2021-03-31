from scrapy.settings import Settings
from scrapy.crawler import CrawlerProcess

from media_scraping import settings
from media_scraping.spiders.leroymerlinru import LeroymerlinruSpider
from urllib import parse

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    search = input('search: ')

    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(LeroymerlinruSpider, search=search)

    process.start()
