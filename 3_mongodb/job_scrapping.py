import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup as bs
import pandas as pd
import datetime


def compensation_formatting(compensation, result):
    c = compensation.text
    if '/месяц' in c:
        c = c.replace('/месяц', '')

    if c.startswith('от'):
        result['min'] = c[3:-4]
        result['max'] = None
        result['currency'] = c[-4:]

    elif c.startswith('до'):
        result['min'] = None
        result['max'] = c[3:-4]
        result['currency'] = c[-4:]

    elif '-' in c or '—' in c:
        tmp = c

        if '-' in tmp:
            tmp = tmp.split('-')
        else:
            tmp = tmp.split('—')

        tmp.append(tmp[1][-4:])
        tmp[1] = tmp[1][:-4]
        result['currency'] = tmp[2].strip()
        result['min'], result['max'] = tmp[0], tmp[1]
    else:
        result['min'], result['currency'] = None, None
        result['max'] = c


def superjob_date_format(date_span, result):
    """
    :param date_span: soup.find date of vacancy published
    :param result: dict
    :return: %d %B %Y
    """
    if date_span is not None:
        date_str = date_span
        date_str += ' ' + str(datetime.date.today().year)
        date_fmt = '%d %b %Y'

        v_date = datetime.datetime.strptime(date_str, date_fmt).date()
        date_formatted = v_date.__format__('%d.%m.%y')
        result['date'] = date_formatted
    else:
        result['date'] = None


def hh_job_parse(vacancy: str, result: list):
    hh_url = f'https://hh.ru/search/vacancy?clusters=true&enable_snippets=true' \
             f'&' \
             f'text={vacancy}' \
             f'&' \
             f'area=1&from=cluster_area&showClusters=true'
    headers = headers_init()
    hh_params = {
        'page': '0',
        'items_on_page': '100',
    }
    while True:
        r = requests.get(hh_url, headers=headers, params=hh_params)

        if r.status_code == 200:
            soup = bs(r.text, 'html.parser')
            vacancy_info = soup.find_all(name='div', attrs={'class': 'vacancy-serp-item'})

            if len(vacancy_info) > 0:
                # print(f'{len(vacancy_info)} vacancies were found on page {hh_params["page"]}')
                pass
            else:
                print('vacancy_info is empty')

            if soup.find('a', {'data-qa': 'pager-next'}) is not None:
                for vacancy in vacancy_info:
                    info = {}
                    title = vacancy.find('a', attrs={'data-qa': "vacancy-serp__vacancy-title"})
                    if title is None:
                        continue
                    info['resource'] = 'hh.ru'
                    info['position'] = title.text
                    info['vacancy_link'] = title['href']
                    compensation = vacancy.find('span', attrs={'data-qa': "vacancy-serp__vacancy-compensation"})
                    if compensation is not None:
                        compensation_formatting(compensation, info)
                    #                         info['compensation'] = str(compensation.text)
                    else:
                        info['min'], info['max'], info['currency'] = None, None, None
                    employer = vacancy.find('a', attrs={'data-qa': "vacancy-serp__vacancy-employer"})
                    if employer is not None:
                        info['employer'] = employer.text
                    else:
                        info['employer'] = None
                    v_date = vacancy.find('span', attrs={'class': "vacancy-serp-item__publication-date_s-only"})
                    if v_date is not None:
                        info['date'] = v_date.text

                    result.append(info)
                hh_params['page'] = str(int(hh_params['page']) + 1)
            else:
                break
        else:
            break
    # print(f'{len(result)} vacancies were parsed from {hh_url}')
    return result


def superjob_parse(vacancy: str, result):
    superjob_url = 'https://www.superjob.ru/vacancy/search/'
    headers = headers_init()
    sj_params = {'keywords': vacancy,
                 'page': '1',
                 'noGeo': '1'}
    while True:
        r = requests.get(superjob_url, headers=headers, params=sj_params)

        if r.status_code == 200:
            soup = bs(r.text, 'html.parser')
            vacancy_info = soup.find_all('div', attrs={'class': 'f-test-search-result-item'})
            if len(vacancy_info) == 0:
                # print('vacancy_info is empty')
                break
            for vacancy in vacancy_info:
                info = {}
                title = vacancy.find('a')
                if title is None:
                    continue
                info['resource'] = 'superjob.ru'
                info['position'] = title.text
                # print(title.text, end='... ')
                employer = vacancy.find('span', attrs={'class': "f-test-text-vacancy-item-company-name"})
                if employer is not None:
                    info['employer'] = employer.text
                else:
                    info['employer'] = None
                info['vacancy_link'] = title['href']
                compensation = vacancy.find('span', attrs={'class': "f-test-text-company-item-salary"})
                if compensation is not None:
                    # func for compensation formatting
                    compensation_formatting(compensation, info)
                else:
                    info['min'], info['max'], info['currency'] = None, None, None
                if soup.find('span', attrs={'class': "_1BOkc"}) is not None:
                    sj_params['page'] = str(int(sj_params['page']) + 1)
                v_date = soup.find('span', attrs={'class': '_3mfro f-test-text-company-item-location '
                                                           '_9fXTd _2JVkc _2VHxz'})
                v_date = v_date.find('span', attrs={'class': '_3mfro _9fXTd _2JVkc _2VHxz'})
                # superjob_date_format(v_date, info)      # не работает :(((
                # print(info['date'])         # ValueError: time data '12 марта 2021' does not match format '%d %B %Y'
                info['date'] = v_date.text
                result.append(info)
            if soup.find('span', attrs={'_1BOkc'}):
                sj_params['page'] = str(int(sj_params['page']) + 1)
            # print(f'{len(result)} vacancies were parsed from {superjob_url}')

        else:
            print(f'response: {r.status_code}')

    return result


def headers_init():
    u = UserAgent()
    driver = u.random
    headers = {
        'User-Agent': driver
    }
    return headers


def parse_total_vacancies(vacancy: str):
    vacancy_str_hh = vacancy.replace(' ', '+')
    vacancy_str_sj = vacancy.replace(' ', '-')

    vacancies = []

    hh_job_parse(vacancy_str_hh, vacancies)
    superjob_parse(vacancy_str_sj, vacancies)
    print(f'{len(vacancies)} vacancies were successfully parsed in general')
    return vacancies


def find_query_data(collection, sal_instance, operator, value: int = None):
    res = []

    if value is not None:
        operator_dict = {'>': '$gt', '<': '$lt', '>=': '$gte', '<=': '$lte', '=': '$eq'}
        query = collection.find({sal_instance: {operator_dict[operator]: value}})
        res.append(query)
    else:
        query = collection.find({'currency': value})
        res.append(query)

    df = pd.DataFrame.from_records(res)
    return df
