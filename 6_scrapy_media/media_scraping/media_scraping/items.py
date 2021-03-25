# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import MapCompose, TakeFirst
import re


def resize_img(img):
    return re.sub('w_\d+,h_\d+', 'w_1200,h_1200', img)


class MediaScrapingItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field()
    name = scrapy.Field(output_processor=TakeFirst())
    images = scrapy.Field(input_processor=MapCompose(resize_img))
    params = scrapy.Field()
    link = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(output_processor=TakeFirst())
    pass

