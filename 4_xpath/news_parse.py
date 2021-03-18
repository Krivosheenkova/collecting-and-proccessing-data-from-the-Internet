from fake_useragent import UserAgent
from pprint import pprint
from lxml import html
import requests
import datetime
from time import sleep
from pymongo import MongoClient

date_fmt = '%Y-%m-%d %H:%M'
headers = {'UserAgent': UserAgent().random}


def parse_news_yandex():
    url = 'https://news.yandex.ru/news/'

    response = requests.get(url, headers=headers)
    root = html.fromstring(response.text)
    news_blocks = root.xpath('''//div[contains (@class, "news-top-flexible-stories")]
                                //a[@class='mg-card__link']''')
    info = []

    for new in news_blocks:
        result = {}
        title = new.xpath(".//text()")

        href = new.xpath("./@href")
        result['title'] = title[0]
        result['href'] = href[0]

        date_source_block = root.xpath('''//div[contains (@class, "news-top-flexible-stories")]
                                          //div[contains (@class, "mg-card__source")]''')
        for item in date_source_block:
            source = item.xpath(".//a[@class='mg-card__source-link']//text()")
            time = item.xpath(".//span[@class='mg-card-source__time']/text()")
            date = str(datetime.date.today()) + ' ' + time[0]

            result['source'] = source[0]
            result['date'] = date

        info.append(result)

    print(f'{url} was parsed successfully')
    return info


def get_date_source(url):
    result = {}

    news_page = requests.get(url, headers=headers)
    root = html.fromstring(news_page.text)
    date_source_block = root.xpath("//div[contains(@class, 'breadcrumbs')]")
    for item in date_source_block:
        date = item.xpath(".//@datetime")[0][:-9]
        d1 = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M")
        date = d1.strftime(date_fmt)
        source = item.xpath(".//span[@class='link__text']/text()")

        result['source'] = source[0]
        result['date'] = date

    return result


def parse_news_mail():
    url = 'https://news.mail.ru/'

    result = []
    response = requests.get(url, headers=headers)
    root = html.fromstring(response.text)
    news_blocks = root.xpath("//td[@class='daynews__main']//a | //td[@class='daynews__items']//a")
    news_list_items = root.xpath("//ul/li[@class='list__item']/a")

    for item in news_blocks:
        info = {}
        title = item.xpath(".//span[contains (@class, 'photo__title')]/text()")
        info['title'] = title[0]
        href = item.xpath("./@href")
        info['href'] = href[0]

        ds = get_date_source(href[0])
        info.update(ds)

        result.append(info)

    for item in news_list_items:
        info = {}

        title = item.xpath("./text()")
        href = item.xpath("./@href")
        info['href'], info['title'] = href[0], title[0]

        ds = get_date_source(href[0])
        info.update(ds)

        result.append(info)

    print(f'{url} was parsed successfully')
    return result


def parse_lenta_ru():
    result = []
    url = 'https://lenta.ru/'
    sleep(1)
    response = requests.get(url, headers=headers)
    root = html.fromstring(response.text)

    news_blocks = root.xpath("""//section[contains (@class, 'b-top7-for-main')]//a[child::time] |                               
                                //section[contains (@class, 'b-yellow-box')]//a""")
    for new in news_blocks:
        info = {}
        title = new.xpath("./text()")[0]
        href = new.xpath("./@href")
        info['title'], info['href'] = title, url + href[0]
        source = new.xpath('//meta[@property="og:title"]/@content')
        info['source'] = source[0]

        news_page = requests.get(url + href[0], headers=headers)
        tmp_root = html.fromstring(news_page.text)
        date_raw = tmp_root.xpath("//div[@class='b-topic__info']//@datetime")[0][:-9]
        d1 = datetime.datetime.strptime(date_raw, "%Y-%m-%dT%H:%M")
        date = d1.strftime(date_fmt)

        info['date'] = date

        result.append(info)
    print(f'{url} was parsed successfully')
    return result


parsed_news = parse_news_mail() + parse_news_yandex() + parse_lenta_ru()
parsed_news = sorted(parsed_news, key=lambda k: k['date'], reverse=True)

client = MongoClient('mongodb://localhost:27017/')
db = client['news']
collection = db['mail_yandex_lenta_news']

for doc in parsed_news:
    collection.replace_one({'href': doc['href']}, doc, upsert=True)


"""
_id': ObjectId('6053c400e5204ef8b7b367c0'),
 'date': '2021-03-19 вчера в 23:59',
 'href': 'https://yandex.ru/news/story/Bajden_proignoriroval_vopros_orazgovore_s...',
 'source': 'Известия',
 'title': 'Байден проигнорировал вопрос о\xa0разговоре с\xa0Путиным'}
{'_id': ObjectId('6053c13dacce4b513d393340'),
 'date': '2021-03-19 вчера в 23:21',
 'href': 'https://yandex.ru/news/story/Belyj_dom_zayavil_chto_Bajden_ne_zhaleet_osvo...',
 'source': 'Известия',
 'title': 'Белый дом заявил, что Байден не жалеет о\xa0своих высказываниях '
          'о\xa0Путине'}
{'_id': ObjectId('6053c724e5204ef8b7b3683b'),
 'date': '2021-03-19 в',
 'href': 'https://yandex.ru/news/story/Belyj_dom_zayavil_chto_Bajden_ne_zhaleet_osvoikh...',
 'source': 'Известия',
 'title': 'Белый дом заявил, что Байден не жалеет о\xa0своих высказываниях '
          'о\xa0Путине'}
{'_id': ObjectId('6053d66ee5204ef8b7b36a82'),
 'date': '2021-03-19 01:33',
 'href': 'https://lenta.ru//news/2021/03/19/wazzzup/',
 'source': 'Лента.Ру',
 'title': 'Россиян предупредили об\xa0опасности использования WhatsApp'}
{'_id': ObjectId('6053d33be5204ef8b7b36911'),
 'date': '2021-03-19 01:15',
 'href': 'https://lenta.ru//news/2021/03/19/ogovorka/',
 'source': 'Лента.Ру',
 'title': 'Байден снова назвал Камалу Харрис президентом'}
{'_id': ObjectId('6053d4d8e5204ef8b7b369c3'),
 'date': '2021-03-19 01:13',
 'href': 'https://news.mail.ru/politics/45614001/',
 'source': 'Коммерсантъ',
 'title': 'Кадыров озадачен словами Пескова об\xa0обращении к\xa0президенту'}
{'_id': ObjectId('6053d33be5204ef8b7b36913'),
 'date': '2021-03-19 01:11',
 'href': 'https://lenta.ru//news/2021/03/19/pomp/',
 'source': 'Лента.Ру',
 'title': 'Помпео прокомментировал слова Байдена в\xa0адрес Путина'}
{'_id': ObjectId('6053d66ee5204ef8b7b36a86'),
 'date': '2021-03-19 01:11',
 'href': 'https://sportmail.ru/news/football-eurocups/45613979/',
 'source': 'Спорт РИА Новости',
 'title': 'Стали известны все клубы, вышедшие в четвертьфинал Лиги Европы'}
"""