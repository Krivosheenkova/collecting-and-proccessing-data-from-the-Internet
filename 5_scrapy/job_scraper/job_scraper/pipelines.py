# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient 
from unicodedata import normalize

MONGO_URL = 'localhost:27017'


class JobScraperPipeline:
    def __init__(self):
        self.client = MongoClient(MONGO_URL)
        self.db = self.client['vacancy']

    def process_item(self, item, spider):
        collection = self.db[spider.name]
        adapter = ItemAdapter(item)
        if spider.name == 'hhru':
            adapter['salary_min'], adapter['salary_max'], adapter['currency'] = \
                self.process_hh_salary(adapter['salary'])
        else:
            adapter['salary_min'], adapter['salary_max'], adapter['currency'] = \
                self.process_sj_salary(adapter['salary'])

        if spider.name == 'hhru':
            adapter['source'] = 'hh.ru'
        else:
            adapter['source'] = 'superjob.ru'
        del adapter['salary']
        try:
            adapter['company'] = ''.join(adapter['company'])
        except TypeError:
            pass
        collection.replace_one({'link': adapter['link']}, adapter.asdict(), upsert=True)
        print('')

    @staticmethod
    def process_hh_salary(salary):
        salary_min, salary_max, currency = None, None, None
        if len(salary) > 1:

            if ('от ' and ' до ') in salary:
                currency = salary[5]
                salary_min = normalize('NFKD', salary[1].replace(' ', ''))
                salary_max = normalize('NFKD', salary[3].replace(' ', ''))

            elif ('от ' in salary) or (' до ' in salary):
                salary_min = salary[1].replace(' ', '')
                salary_max = None
                currency = salary[3]
                salary_min = normalize('NFKD', salary_min)

            elif not ('от ' in salary) or (' до ' in salary):
                salary_max = salary[1].replace(' ', '')
                salary_min = None
                currency = salary[3]
                salary_max = normalize('NFKD', salary_max)

        return salary_min, salary_max, currency

    @staticmethod
    def process_sj_salary(salary):
        salary_min, salary_max, currency = None, None, None

        if len(salary) > 1:
            if '—' in salary:
                salary_min = salary[0].replace(' ', '')
                salary_max = salary[4].replace(' ', '')
                currency = salary[6]
            elif 'от' in salary:
                salary_min = salary[2][:-4].replace(' ', '')
                currency = salary[2][-4:]
                salary_max = None
            elif 'до' in salary:
                salary_max = salary[2][:-4].replace(' ', '')
                salary_min = None
                currency = salary[2][-4:]
            else:
                salary_min = salary[0].replace(' ', '')
                salary_max = salary_min
                currency = None

        return salary_min, salary_max, currency
