"""
1. Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB и реализовать функцию,
    записывающую собранные вакансии в созданную БД.
2. Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой больше введённой суммы,
    а также использование одновременно мин/макс зарплаты.
    Дополнительно - возможность выбрать вакансии без указанных зарплат
3. Написать функцию, которая будет добавлять в вашу базу данных только новые вакансии с сайта.
"""
from pymongo import MongoClient

import job_scrapping

vacancy = input('enter vacancy name> ')
parsed_vacancies = job_scrapping.parse_total_vacancies(vacancy)

MONGO_URI = "localhost:27017"
MONGO_DB = "job_scrapping"

with MongoClient(MONGO_URI) as client:
    db = client[MONGO_DB]
    vacancies = db['vacancies_hh_sj']

    for v in parsed_vacancies:
        vacancies.replace_one({'vacancy_link': v['vacancy_link']}, v, upsert=True)

    df = job_scrapping.find_query_data(vacancies, 'max', '>', 6000)
    # print(df)