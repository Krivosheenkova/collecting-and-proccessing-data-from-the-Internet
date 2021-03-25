# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


import mimetypes
import os
import re
from datetime import date

import scrapy
from itemadapter import ItemAdapter
from pymongo import MongoClient
from scrapy.pipelines.images import ImagesPipeline
from transliterate import translit

MONGO_URL = 'localhost:27017'


class MediaScrapingImagesPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['images']:
            for img in item['images']:
                try:
                    yield scrapy.Request(img)
                except Exception as e:
                    print(e)

    def item_completed(self, results, item, info):
        if results:
            item['images'] = [itm[1] for itm in results]
        return item

    def file_path(self, request, response=None, info=None, *, item=None):
        name = item['name']
        symbols = ['«', '»']
        for sym in symbols:
            name = name.replace(sym, '')
        name = str(translit(name.replace(' ', '_'), 'ru', reversed=True))
        search = name[:name.index('_')]
        media_ext = os.path.splitext(request.url)[1]
        if media_ext not in mimetypes.types_map:
            media_ext = ''
            media_type = mimetypes.guess_type(request.url)[0]
            if media_type:
                media_ext = mimetypes.guess_extension(media_type)
        return f'{search}{date.today()}/{name}{media_ext}'


def clean_params(params: list):
    if params:
        return [re.sub("^\s+|\n|\r|\s+$", '', param) for param in params]


def str_to_float(string):
    if string:
        return float(string.replace(' ', ''))


class MediaScrapingPipeline:
    def __init__(self):
        self.client = MongoClient(MONGO_URL)
        self.db = self.client['leroy']

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        collection = self.db[spider.name]

        if adapter['params']:
            adapter['params'] = clean_params(adapter['params'])
            adapter['params'] = self.process_params(adapter['params'])
        adapter['price'] = str_to_float(adapter['price'])
        collection.update_one({'link': adapter['link']}, {'$set': adapter.asdict()}, upsert=True)
        return item

    def process_params(self, params):
        if params:
            dt = [params[i] for i in range(len(params)) if i % 2 == 0]
            dd = [params[i] for i in range(len(params)) if i % 2 != 0]

            return {dt: dd for dt, dd in zip(dt, dd)}
