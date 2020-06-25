import requests
import json
from pprint import pprint


header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
          'Accept': '*/*'}

main_link = 'https://api.github.com/users/SemenenkoRE/repos'

response = requests.get(main_link, headers=header)

# 1 способ

# data = response.json()

# 2 способ (выдает json в виде словоря в одну строку)

status = response.status_code
print(f'Статус запроса: {status} \n *******************')

data = json.loads(response.text)

pprint(data)