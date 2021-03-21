from fake_useragent import UserAgent
from pprint import pprint
from lxml import html
import requests
import datetime
from time import sleep
from pymongo import MongoClient

date_fmt = '%Y-%m-%d %H:%M'
headers = {'UserAgent': UserAgent().random}

client = MongoClient('mongodb://localhost:27017/')
db = client['news']
collection = db['mail_yandex_lenta_news']


def get_value(elem):
    if len(elem) > 0:
        return elem[0]
    print(elem)


def parse_news_yandex():
    url = 'https://news.yandex.ru/news/'

    response = requests.get(url, headers=headers)
    root = html.fromstring(response.text)
    news_blocks = root.xpath('''//div[contains (@class, "news-top-flexible-stories")]
                                //a[@class='mg-card__link']''')
    for new in news_blocks:
        info = {}
        title = new.xpath(".//text()")

        href = new.xpath("./@href")
        info['title'] = get_value(title)
        info['href'] = get_value(href)

        date_source_block = root.xpath('''//div[contains (@class, "news-top-flexible-stories")]
                                          //div[contains (@class, "mg-card__source")]''')
        for item in date_source_block:
            source = item.xpath(".//a[@class='mg-card__source-link']//text()")
            time = item.xpath(".//span[@class='mg-card-source__time']/text()")
            date = str(datetime.date.today()) + ' ' + get_value(time).replace(' вчера ',  '')
            info['source'] = get_value(source)
            info['date'] = date

        collection.replace_one({'href': info['href']}, info, upsert=True)

    print(f'{url} was parsed successfully\nresults recorded to {db}')


def get_date_source(url):
    result = {}

    news_page = requests.get(url, headers=headers)
    root = html.fromstring(news_page.text)
    date_source_block = root.xpath("//div[contains(@class, 'breadcrumbs')]")
    for item in date_source_block:
        date_raw = item.xpath(".//@datetime")
        d1 = datetime.datetime.strptime(get_value(date_raw)[:-9], "%Y-%m-%dT%H:%M")
        date = d1.strftime(date_fmt)
        source = item.xpath(".//span[@class='link__text']/text()")

        result['source'] = get_value(source)
        result['date'] = date

    return result


def parse_news_mail():
    url = 'https://news.mail.ru/'

    response = requests.get(url, headers=headers)
    root = html.fromstring(response.text)
    news_blocks = root.xpath("//td[@class='daynews__main']//a | //td[@class='daynews__items']//a")
    news_list_items = root.xpath("//ul/li[@class='list__item']/a")

    for item in news_blocks:
        info = {}
        title = item.xpath(".//span[contains (@class, 'photo__title')]/text()")
        info['title'] = get_value(title)
        href = item.xpath("./@href")
        info['href'] = get_value(href)

        ds = get_date_source(info['href'])
        info.update(ds)

        collection.replace_one({'href': info['href']}, info, upsert=True)

    for item in news_list_items:
        info = {}

        title = item.xpath("./text()")
        href = item.xpath("./@href")
        info['href'], info['title'] = get_value(href), get_value(title)

        ds = get_date_source(info['href'])
        info.update(ds)

        collection.replace_one({'href': info['href']}, info, upsert=True)

    print(f'{url} was parsed successfully\nresults recorded to {db}')


def parse_lenta_ru():

    url = 'https://lenta.ru/'
    sleep(1)
    response = requests.get(url, headers=headers)
    root = html.fromstring(response.text)

    news_blocks = root.xpath("""//section[contains (@class, 'b-top7-for-main')]//a[child::time] |                               
                                //section[contains (@class, 'b-yellow-box')]//a""")
    for new in news_blocks:
        info = {}
        title = new.xpath("./text()")
        href = new.xpath("./@href")
        info['title'], info['href'] = get_value(title), url + get_value(href)
        source = new.xpath('//meta[@property="og:title"]/@content')
        info['source'] = get_value(source)

        news_page = requests.get(info['href'], headers=headers)
        tmp_root = html.fromstring(news_page.text)
        date_raw = tmp_root.xpath("//div[@class='b-topic__info']//@datetime")[0][:-9]
        d1 = datetime.datetime.strptime(date_raw, "%Y-%m-%dT%H:%M")
        date = d1.strftime(date_fmt)
        info['date'] = date

        collection.replace_one({'href': info['href']}, info, upsert=True)

    print(f'{url} was parsed successfully\nresults recorded to {db}')


parse_news_mail()
parse_news_yandex()
parse_lenta_ru()


"""
{'date': '2021-03-19 11:43',
 'href': 'https://news.mail.ru/society/45613754/',
 'source': 'Аргументы и факты',
 'title': 'Как закон о\xa0валежнике обернулся уголовными делами'}
{'date': '2021-03-19 22:59',
 'href': 'https://yandex.ru/news/story/Bajden_poobeshhal_snova_pogovorit_sPutinym--7...',
  'source': 'Известия',
 'title': 'Байден пообещал снова поговорить с\xa0Путиным'}
{'date': '2021-03-19 22:59',
 'href': 'https://yandex.ru/news/story/Merkel_ne_isklyuchila_zakupku_Germaniej_vakciny_Sputnik...',
  'source': 'Известия',
 'title': 'Меркель не исключила закупку Германией вакцины «Спутник V»'}
{'date': '2021-03-19 22:59',
 'href': 'https://yandex.ru/news/story/EHlektronnye_pasporta_vMoskve_nachnut_oformlyat_s1_dekabrya_2021_g...',
  'source': 'Известия',
 'title': 'Электронные паспорта в\xa0Москве начнут оформлять с\xa01 декабря '
          '2021 года'}
{'date': '2021-03-19 22:59',
 'href': 'https://yandex.ru/news/story/Bank_Rossii_povysil_klyuchevuyu_stavku_do45_procenta_godovykh--...',
  'source': 'Известия',
 'title': 'Банк России повысил ключевую ставку до\xa04,5 процента годовых'}
{'date': '2021-03-19 22:59',
 'href': 'https://yandex.ru/news/story/Propavshaya_sradarov_NATO_podlodka_CHF_ne_preryvala_svyaz_skomando...',
 'source': 'Известия',
 'title': 'Пропавшая с\xa0радаров НАТО подлодка ЧФ не прерывала связь с\xa0'
          'командованием'}

{'date': '2021-03-19 22:26',
 'href': 'https://lenta.ru//news/2021/03/19/zaharova/',
 'source': 'Лента.Ру',
 'title': 'Захарова прокомментировала падение Байдена при подъеме на\xa0борт '
          'номер один'}
"""