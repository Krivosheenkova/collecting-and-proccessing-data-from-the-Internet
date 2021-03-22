# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class JobScraperItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field()
    source = scrapy.Field()
    title = scrapy.Field()
    link = scrapy.Field()
    company = scrapy.Field()
    salary_min = scrapy.Field()
    salary_max = scrapy.Field()
    currency = scrapy.Field()
    salary = scrapy.Field()
    pass
