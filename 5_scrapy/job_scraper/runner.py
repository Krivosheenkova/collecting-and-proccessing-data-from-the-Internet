from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from job_scraper.spiders.hhru import HHruSpider
from job_scraper.spiders.sjru import SjruSpider
from job_scraper import settings


if __name__ == "__main__":
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(HHruSpider)
    process.crawl(SjruSpider)

    process.start()
