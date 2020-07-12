from bs4 import BeautifulSoup as bs
import requests as r
from pprint import pprint
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client['vacancies_db']


vacancies_db = db.vacancies_db



req_link = 'https://hh.ru/search/vacancy?area=1&st=searchVacancy&text=Data+science&fromSearch=true&from=suggest_post'

header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36', 'Accept': '*/*'}

response = r.get(req_link, headers=header).text

soup = bs(response, 'lxml')

                                                  # Создается список, в который в дальнейшем будут включаться
                                                  # id добавленных объектов. Но на момент начала работы, мы его
                                                  # заполняем значениями _id, котороые уже содержаться в БД

list_id = []

for el in vacancies_db.find({}):

    list_id.append(el['_id'])


                                                  # Создается переменная last_page, содержащая информацию о числе
                                                  # страниц с вакансиями, и в диапазоне которого будет проводится поиск

last_page = int(soup.find_all('a', {'class': 'bloko-button HH-Pager-Control'})[-1]['data-page'])


for n in range(last_page):                         # создан цикл, который пробегаеться по страницам hh.ru с
                                                   # нужным запросом

                                                   # Создается переменная vacancies_block_hh содержащая объект soup
                                                   # с блоками объявлений. Далее создается переменная vacancies_list_hh
                                                   # содержащая список необходимых для парсинга тегов

    vacancies_block_hh = soup.find('div', {'class': 'vacancy-serp'})
    vacancies_list_hh = vacancies_block_hh.find_all('div', {'class': 'vacancy-serp-item'})


    for vacancy in vacancies_list_hh:              # создан цикл, который пробегает по всем блокам вакансий
                                                   # на текущей странице вакансий

                                                   # Извлекаем ссылку на вакансию и извлекаем ID из ссылки

        ref_vacancy = vacancy.find('a', {'class': 'bloko-link HH-LinkModifier'})['href']
        id = ref_vacancy[22:30]

                                                   # Проверка наличия ID в БД, если такой ID имеется, то пропускаем
                                                   # дальнейший код, иначе ID добавляется в список с ID
                                                   # и продолжается сбор данных
        if id in list_id:

            continue


        list_id.append(id)

                                                   # далее создаются переменные:
                                                   # зарплата (от), зарплата (до), валюта, название вакансии
        pay_untill = ''
        pay_after = ''
        currency = ''
        name_vacancy = vacancy.find('a', {'class': 'bloko-link HH-LinkModifier'}).getText()

                                                   # Создается переменная name_company, чтобы в дальнейшем проверить,
                                                   # что данный тег не пустой

        name_company = vacancy.find('a', {'class': 'bloko-link bloko-link_secondary'})

                                                   # Осуществляем проверку данного объекта vacancy на то, что это не
                                                   # рекламный блок, типа "Получайте новые вакансии по этому запросу.
                                                   # На почту / мессенджер". В таком случае берем из него название
                                                   # компании и ссылку на описание компании. Иначе, т.е. если блок
                                                   # рекламный (посвещен не вакансии), пропускаем дальнейшее извелечение данных

        if name_company is not None:

            name_company = vacancy.find('a', {'class': 'bloko-link bloko-link_secondary'}).getText()
            ref_company = 'https://hh.ru/' + vacancy.find('a', {'class': 'bloko-link bloko-link_secondary'})['href']

        else:

            continue

                                                     # создается переменная, содержащая информацию о ЗП. Информация
                                                     # находится в неочищенном от предлогов, пробелов, дефисов виде

        untreated_pay = vacancy.find('div', {'class': 'vacancy-serp-item__sidebar'}).getText()

                                                     # далее идет обработка зарплаты в неочищенном виде

                                                     # обработка информации о ЗП, содержащей "-", эта информациия
                                                     # содержит как ЗП (от), так и ЗП (до)

        if '-' in untreated_pay:


            for el in untreated_pay[:untreated_pay.index('-')]:  # перебор символов до "-"

                if el.isdigit():
                    pay_untill = f'{pay_untill}{el}'  # формирование ЗП в виде строки


            for el in untreated_pay[untreated_pay.index('-') + 1:]:  # Перебор символов после "-"

                if el.isdigit():
                    pay_after = f'{pay_after}{el}'   # формирование ЗП в виде строки

                if not el.isdigit() and el != " ":   # ввод условия по которому обрабатывается только валюта

                    currency = (f'{currency}{el}').replace('\xa0', '')  # формирование валюты в виде строки


            pay_untill, pay_after = int(pay_untill), int(pay_after)  # перевод валюты в численное значение


                                                      # обработка информации о ЗП, в которой содержится информации о ЗП (от)

        if untreated_pay[:2] == 'от':


            for el in untreated_pay[3:]:


                if el.isdigit():
                    pay_after = f'{pay_after}{el}'
                    pay_untill = 'Null'

                if not el.isdigit() and el != " ":
                    currency = (f'{currency}{el}').replace('\xa0', '')

                                                       # обработка информации о ЗП, в которой содержится информации о ЗП (до)

        if untreated_pay[:2] == 'до':


            for el in untreated_pay[3:]:


                if el.isdigit():
                    pay_untill = f'{pay_untill}{el}'
                    pay_after = 'Null'

                if not el.isdigit() and el != " ":
                    currency = (f'{currency}{el}').replace('\xa0', '')


                                                       # обработка информации о ЗП, в случае когда она отсутствует

        if untreated_pay == '':
            pay_untill = 'Null'
            pay_after = 'Null'
            currency = 'Null'
                                                       # передается БД полученная ранее информация о вакансии в
                                                       # виде переменных. Хотя повторяющиеся значения не попадают
                                                       # в базу данных, исключаем непредвиденную ошибку.

        try:

            vacancies_db.insert_one({'Название вакансии': name_vacancy, 'Портал': 'hh.ru', 'Ссылка на вакансию': ref_vacancy,
                                 'Название компании': name_company, 'Ссылка на компанию': ref_company,
                                 'Зарплата (до)': pay_untill, 'Зарплата (от)': pay_after, 'Валюта': currency, '_id': id})

        except:

            pass
                                                        # после парсинга текущей страницы
                                                        # получаем окончание ссылки, ссылающаяся на следующую страницу

    next_page_ref = soup.find('a', {'class': 'bloko-button HH-Pager-Controls-Next HH-Pager-Control'})['href']

                                                        # формируется ссылка на следующую страницу
                                                        # после той, которую мы обработали

    req_link = f'https://hh.ru/{next_page_ref}'
                                                        # формируется текст нового запроса

    response = r.get(req_link, headers=header).text

                                                        # из текста нового запроса формируется новый объект soup
                                                        # который в следующем цикле будет аналогичным образом обработан
    soup = bs(response, 'lxml')



# ПАРСИНГ superjob.ru

req_link = 'https://www.superjob.ru/vacancy/search/?keywords=Data%20science&geo%5Bt%5D%5B0%5D=4'

response = r.get(req_link, headers=header).text

soup = bs(response, 'lxml')


# vacancies_block_sj = soup.find('div', {'class': '_1ID8B'})
# vacancies_list_sj = vacancies_block_sj.find_all('div', {'class': 'f-test-vacancy-item'})

                                                        # т.к. на superjob.ru может быть не больше одного листа с вакансиями
                                                        # предусмотрено условие, проверяющее что кнопка далее имеется
                                                        # иначе цикл будет повторяться один раз

last_page = None


if soup.find('span', {'class': '_3IDf'}):

    last_page = soup.find('span', {'class': '_3IDf'}).getText()

else:

    last_page = 1


for n in range(last_page):                               # создан цикл, который пробегает по страницам superjob.ru с нужным запросом


    vacancies_block_sj = soup.find('div', {'class': '_1ID8B'})
    vacancies_list_sj = vacancies_block_sj.find_all('div', {'class': 'f-test-vacancy-item'})


    for vacancy in vacancies_list_sj:

        ref_vacancy = 'https://www.superjob.ru/' + vacancy.find('a', {'class': 'icMQ_'})['href']
        id = ref_vacancy[-13:-5]


        if id in list_id:

            continue

        list_id.append(id)
                                                         # Т.к. ID прошел проверку, начинаем сбор и обратоку
                                                         # по текущему блоку вакансии

                                                         # далее создаются переменные:
                                                         # зарплата (от), зарплата (до), валюта, название вакансии

        name_company = vacancy.find('span', {'class': 'f-test-text-vacancy-item-company-name'}).getText()


        if name_company is not None:

            ref_company = 'https://www.superjob.ru/' + vacancy.find('a', {'class': '_205Zx'})['href']

        else:

            continue


        pay_untill = ''
        pay_after = ''
        currency = ''
        name_vacancy = vacancy.find('a', {'class': 'icMQ_'}).getText()


        untreated_pay = vacancy.find('span', {'class': 'PlM3e'}).getText().replace(u'\xa0', u' ')


        if '-' in untreated_pay:


            for el in untreated_pay[:untreated_pay.index('-')]:  # перебор символов до "-"

                if el.isdigit():

                    pay_untill = f'{pay_untill}{el}'    # формирование ЗП в виде строки


            for el in untreated_pay[untreated_pay.index('-') + 1:]:  # Перебор символов после "-"


                if el.isdigit():

                    pay_after = f'{pay_after}{el}'      # формирование ЗП в виде строки

                if not el.isdigit() and el != " ":      # ввод условия по которому обрабатывается только валюта

                    currency = f'{currency}{el}'        # формирование валюты в виде строки

            pay_untill, pay_after = int(pay_untill), int(pay_after)  # перевод валюты в численное значение


                                                        # обработка информации о ЗП, в которой содержится информации о ЗП (от)

        if untreated_pay[:2] == 'от':


            for el in untreated_pay[3:]:

                if el.isdigit():

                    pay_after = f'{pay_after}{el}'
                    pay_untill = 'Null'

                if not el.isdigit() and el != " ":

                    currency = f'{currency}{el}'

                                                        # обработка информации о ЗП, в которой содержится информации о ЗП (до)

        if untreated_pay[:2] == 'до':


            for el in untreated_pay[3:]:

                if el.isdigit():
                    pay_untill = f'{pay_untill}{el}'
                    pay_after = 'Null'

                if not el.isdigit() and el != " ":
                    currency = f'{currency}{el}'


                                                        # обработка информации о ЗП, в случае когда она отсутствует

        if untreated_pay == 'По договорённости':
            pay_untill = 'Null'
            pay_after = 'Null'
            currency = 'Null'

        try:

            vacancies_db.insert_one({'Название вакансии': name_vacancy, 'Портал': 'superjob.ru', 'Ссылка на вакансию': ref_vacancy,
                                 'Название компании': name_company, 'Ссылка на компанию': ref_company,
                                 'Зарплата (до)': pay_untill, 'Зарплата (от)': pay_after, 'Валюта': currency, '_id': id})

        except:

            pass


    if last_page != 1:
        next_page_ref = soup.find('a', {'class': 'f-test-link-Dalshe'})['href']

                                                        # формируется ссылка на следующую страницу после той, которую мы обработали

    req_link = f'https://www.superjob.ru/{next_page_ref}'

                                                        # формируется текст нового запроса

    response = r.get(req_link, headers=header).text

                                                        # из текста нового запроса формируется новый объект soup
                                                        # который в следующем цикле будет аналогичным образом обработан

    soup = bs(response, 'lxml')




