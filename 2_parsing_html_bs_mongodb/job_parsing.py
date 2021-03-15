#!/usr/bin/python

import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup as bs
import pandas as pd
# import argparse
import sys
import datetime

# parser = argparse.ArgumentParser()
# parser.add_argument('vacancy_name', help='Find a job that you always wanted')
# vacancy_name = parser.parse_args()                                                  # response: 404


# vacancy_name = input('enter vacancy name to search: ')
# vacancy_name_hh = str(vacancy_name).replace(' ', '+')
# vacancy_name_sj = str(vacancy_name).replace(' ', '-')

if __name__ == "__main__":
    if len(sys.argv) == 2:
        vacancy_name = sys.argv[1]
        vacancy_name_hh = str(vacancy_name).replace(' ', '+')
        vacancy_name_sj = str(vacancy_name).replace(' ', '-')

    else:
        print("unexpected input, run in terminal 'python3 [/path/to/filename.py] 'vacancy_name'")

        sys.exit(1)


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
        date_str = date_span.text
        date_str += ' ' + str(datetime.date.today().year)
        date_fmt = '%d %B %Y'

        v_date = datetime.datetime.strptime(date_str, date_fmt).date()
        date_formatted = v_date.__format__('%d.%m.%y')
        result['date'] = date_formatted
    else:
        result['date'] = None


hh_url = f'https://hh.ru/search/vacancy?clusters=true&enable_snippets=true' \
         f'&' \
         f'text={vacancy_name_hh}' \
         f'&' \
         f'area=1&from=cluster_area&showClusters=true'

superjob_url = f'https://www.superjob.ru/vakansii/{vacancy_name_sj}.html?geo%5Bt%5D%5B0%5D=4'

u = UserAgent()
driver = u.random
headers = {
    'User-Agent': driver
}
hh_params = {
    # 'area': '1',
    # 'clusters': True,
    # 'enable_snippets': True,
    # 'text': vacancy_name_hh,
    # 'showClusters': True,          # c base_url почему-то не получается, 404.
    # 'st': 'searchVacancy',
    'page': '0',
    'items_on_page': '100',
}
sj_params = {
    'page': '0'
}


def hh_job_parse(url, result: list):
    while True:
        r = requests.get(url, headers=headers, params=hh_params)

        if r.status_code == 200:
            soup = bs(r.text, 'html.parser')
            vacancy_info = soup.find_all(name='div', attrs={'class': 'vacancy-serp-item'})

            if len(vacancy_info) > 0:
                print(f'{len(vacancy_info)} vacancies were found on page {hh_params["page"]}')
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

                    else:
                        info['date'] = None
                    result.append(info)
                hh_params['page'] = str(int(hh_params['page']) + 1)
            else:
                break
        else:
            break
    return result


def superjob_parse(url, result):
    while True:
        r = requests.get(url, headers=headers, params=sj_params)

        if r.status_code == 200:
            soup = bs(r.text, 'html.parser')
            vacancy_info = soup.find_all('div', attrs={'class': 'f-test-search-result-item'})
            if len(vacancy_info) == 0:
                print('vacancy_info is empty')
                break
            for vacancy in vacancy_info:
                info = {}
                title = vacancy.find('a')
                if title is None:
                    continue
                info['resource'] = 'superjob.ru'
                info['position'] = title.text
                print(title.text, end='... ')
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
                # superjob_date_format(date, info)      # не работает :(((
                # print(info['date'])         # ValueError: time data '12 марта 2021' does not match format '%d %B %Y'
                info['date'] = v_date.text
                result.append(info)
            else:
                break
        else:
            print(f'response: {r.status_code}')
    return result


vacancies = []
hh_job_parse(hh_url, vacancies)
superjob_parse(superjob_url, vacancies)
vacancies_df = pd.DataFrame.from_records(vacancies)
csv_name = f'vacancies_{vacancy_name.replace(" ", "_")}_{datetime.date.today()}.csv'
vacancies_df.to_csv(csv_name)

print(f'\n{len(vacancies_df)} vacancies were successfully recorded to {csv_name}')
