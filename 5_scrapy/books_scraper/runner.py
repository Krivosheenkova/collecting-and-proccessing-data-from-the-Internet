from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from books_scraper.spiders.labirintru import LabirintruSpider
from books_scraper.spiders.book24ru import Book24ruSpider
from books_scraper import settings


if __name__ == "__main__":
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(LabirintruSpider)
    process.crawl(Book24ruSpider)

    process.start()
