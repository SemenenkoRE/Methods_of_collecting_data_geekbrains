from bs4 import BeautifulSoup as bs
import requests as r
from pprint import pprint


main_link = 'https://hh.ru/search/vacancy?clusters=true&area=1&enable_snippets=true&salary=&st=searchVacancy&text='

header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
          'Accept': '*/*'}

_profession = 'Data+science'

link_request = f'{main_link}{_profession}&fromSearch=true'


response = r.get(link_request, headers=header).text

soup = bs(response, 'lxml')

# pprint(soup)



for n in range(len(soup.find_all('a', {'class': 'bloko-link HH-LinkModifier'}))):

    n = str(n)
    name_vacancy = soup.find('a', {'class': 'bloko-link HH-LinkModifier', 'data-position': n}).get_text()
    ref_vac = soup.find('a', {'class': 'bloko-link HH-LinkModifier', 'data-position': n})['href']
    company_name = soup.find('a', {'class': 'bloko-link HH-LinkModifier', 'data-position': n}).parent.parent.parent.parent.parent.parent.findChildren(recursive=False)[3].getText()


    pay_from = ''
    pay_untill = ''
    pay_between_from = ''
    pay_between_untill = ''

    if soup.find('a', {'class': 'bloko-link HH-LinkModifier', 'data-position': n}).parent.parent.parent.parent.parent.findChildren(recursive=False)[1].getText()[0] == 'о':

        for el in soup.find('a', {'class': 'bloko-link HH-LinkModifier', 'data-position': n}).parent.parent.parent.parent.parent.findChildren(recursive=False)[1].getText():

            if el.isdigit():

                pay_from = f'{pay_from}{el}'


    elif soup.find('a', {'class': 'bloko-link HH-LinkModifier', 'data-position': n}).parent.parent.parent.parent.parent.findChildren(recursive=False)[1].getText()[0] == 'д':

        for el in soup.find('a', {'class': 'bloko-link HH-LinkModifier', 'data-position': n}).parent.parent.parent.parent.parent.findChildren(recursive=False)[1].getText():

            if el.isdigit():

                pay_untill = f'{pay_untill}{el}'


    elif soup.find('a', {'class': 'bloko-link HH-LinkModifier', 'data-position': n}).parent.parent.parent.parent.parent.findChildren(recursive=False)[1].getText()[0].isdigit():

        i = 0

        for el in soup.find('a', {'class': 'bloko-link HH-LinkModifier', 'data-position': n}).parent.parent.parent.parent.parent.findChildren(recursive=False)[1].getText():

            if el.isdigit() and i == 0:

                pay_between_from = f'{pay_between_from}{el}'

            if not el.isdigit():

                if el != '-':

                    continue

                else:

                    i += 1
                    continue

            if el.isdigit() and i == 1:

                pay_between_untill = f'{pay_between_untill}{el}'



    print(f'№{int(n)+1} - Название вакансии: {name_vacancy}\nссылка: {ref_vac}\nзарплата (до): {pay_untill}\nзарплата (от): {pay_from}\nзарплата: {pay_between_from}-{pay_between_untill}\nназвание компании: {company_name}\n')




