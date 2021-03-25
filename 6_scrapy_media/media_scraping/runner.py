from scrapy.settings import Settings
from scrapy.crawler import CrawlerProcess

from media_scraping import settings
from media_scraping.spiders.leroymerlinru import LeroymerlinruSpider
from urllib import parse
"""
1) Взять любую категорию товаров на сайте Леруа Мерлен. Собрать с использованием ItemLoader следующие данные:
● название;
● все фото;
● параметры товара в объявлении(не часть HTML!);
● ссылка;
● цена.

С использованием output_processor и input_processor реализовать очистку и преобразование данных. 
Цены должны быть в виде числового значения.

С сохранением в MongoDB!
Без дубликатов!

2)Написать универсальный обработчик характеристик товаров, 
который будет формировать данные вне зависимости от их типа и количества.

3)Реализовать хранение скачиваемых файлов в отдельных папках, каждая из которых должна соответствовать собираемому товару
"""
if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    search = input('search: ')

    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(LeroymerlinruSpider, search=search)

    process.start()
