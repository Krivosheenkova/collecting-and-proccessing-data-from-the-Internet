"""
Изучить список открытых API. Найти среди них любое, требующее авторизацию (любого типа). Выполнить запросы к нему,
пройдя авторизацию через curl, Postman, Python.Ответ сервера записать в файл (приложить скриншот для Postman и curl)
"""
import requests
from fake_useragent import UserAgent
import json

api_key = '50551cce8939e186906838d29a6ece0f'
u = UserAgent().random
# token = "7z1Tz_0E-vHe2s5vbVp0vpDCr6cKPvCl"
# http://www.last.fm/api/auth/?api_key=50551cce8939e186906838d29a6ece0f&token=7z1Tz_0E-vHe2s5vbVp0vpDCr6cKPvCl
headers = {'UserAgent': u}


def get_top_artist_by_country(country):

    url = f'http://ws.audioscrobbler.com/2.0/?method=geo.gettopartists&country={country.lower()}' \
          f'&api_key={api_key}&format=json'
    r = requests.get(url, headers=headers)
    return r


r = get_top_artist_by_country('Sweden')

with open('lastfm_response.json', 'w') as f:
    json.dump(r.json(), f, sort_keys=True, indent=4)


print('Done')