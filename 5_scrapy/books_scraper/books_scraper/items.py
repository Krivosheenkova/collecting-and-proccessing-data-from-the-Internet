# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BooksScraperItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field()
    title = scrapy.Field()
    link = scrapy.Field()
    author = scrapy.Field()
    price = scrapy.Field()
    price_new = scrapy.Field()
    currency = scrapy.Field()
    rate = scrapy.Field()

    pass
