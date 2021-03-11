import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup as bs
import pandas as pd

hh_url = 'https://hh.ru/search/vacancy?clusters=true&enable_snippets=true&text=data+scientist&' \
      'area=1&from=cluster_area&showClusters=true'
superjob_url = 'https://www.superjob.ru/vakansii/data-scientist.html?geo%5Bt%5D%5B0%5D=4'

u = UserAgent()
driver = u.random
headers = {
    'User-Agent': driver
}
params = {
    # 'area': '1',
    # 'clusters': True,
    # 'enable_snippets': True,
    # 'text': 'data+scientist',
    # 'showClusters': True,          # c base_url почему-то не получается, 404.
    # 'st': 'searchVacancy',
    'page': '0',
    'items_on_page': '100',
}


def hh_job_parse(url, result: list):
    while True:
        r = requests.get(url, headers=headers, params=params)

        if r.status_code == 200:
            soup = bs(r.text, 'html.parser')
            vacancy_info = soup.find_all(name='div', attrs={'class': 'vacancy-serp-item'})

            if len(vacancy_info) > 0:
                pass
#                 print(f'{len(vacancy_info)} vacancies were found on page {params["page"]}')
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
                        info['compensation'] = str(compensation.text)
                    else:
                        info['compensation'] = ' - '
                    employer = vacancy.find('a', attrs={'data-qa': "vacancy-serp__vacancy-employer"})
                    if employer is not None:
                        info['employer'] = employer.text
                    else:
                        info['employer'] = ' - '
                    result.append(info)
                params['page'] = str(int(params['page']) + 1)
            else:
                break
        else:
            break
    return result


def superjob_parse(url, result):
    while True:
        r = requests.get(url, headers=headers)

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
                employer = vacancy.find('span', attrs={'class': "f-test-text-vacancy-item-company-name"})
                if employer is not None:
                    info['employer'] = employer.text
                else:
                    info['employer'] = ' - '
                info['vacancy_link'] = title['href']
                compensation = vacancy.find('span', attrs={'class': "f-test-text-company-item-salary"})
                if compensation is not None:
                    info['compensation'] = str(compensation.text)
                else:
                    info['compensation'] = ' - '

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
print(vacancies_df.sort_values(by='compensation', ascending=False).head(10))
