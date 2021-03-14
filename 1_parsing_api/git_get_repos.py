"""
Посмотреть документацию к API GitHub, разобраться как вывести список репозиториев
для конкретного пользователя, сохранить JSON-вывод в файле *.json.
"""
import requests
import json
from pprint import pprint
url = 'https://api.github.com'
usr = 'krivosheenkova'
r = requests.get(f'{url}/users/{usr}/repos')
pprint([_['name'] for _ in r.json()])
with open('git_response.json', 'w') as f:
    json.dump(r.json(), f)








