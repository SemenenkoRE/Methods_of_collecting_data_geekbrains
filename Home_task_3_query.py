from bs4 import BeautifulSoup as bs
import requests as r
from pprint import pprint
from pymongo import MongoClient

client = MongoClient('localhost', 27017)

db = client['vacancies_db']


vacancies_db = db.vacancies_db

# Посмотреть полное содержимое базы данных

for vacancy in vacancies_db.find({}):

    pprint(vacancy)

# !!! Удалить все содержимое базы данных

# vacancies_db.delete_many({})

# Функция запрашивает у пользователя информацию о валюте и размере оклада в ней.
# Указанные значения заполняют список и будут в дальнейшем переданы другой (локальной)
# функции, которая создает запрос на страницу центро банка, извлекает из нее курс руб/доллар
# и запрашивает у БД вакансии с ЗП соответствующе запросу пользователя как в рублях, так и в долларах


# Создается список для заполнения его требованиями пользователя

# user_pay = []

# Создается функция с именными аргументами, которые заполняет пользователь

def values_for_func(our_cur=input(f'Выбирете валюту рубл. / доллар (нажмите r / d): '),
                    our_pay=input(f'Введите начальное значение ЗП в выбранной валюте: ')):

    user_pay = []

# Открывается цикл, который обязывает пользователя ввести данные корректно, исли это не сделано сразу

    while True:

# Обрабатывается последующий код для избежания ошибки ValueError

        try:

            if our_cur == 'r' or our_cur == 'd':

                user_pay.append(our_cur)
                user_pay.append(int(our_pay))

            else:

                while our_cur != 'r' or our_cur != 'd':

                    print(f'\nУказанное значение валюты: {our_cur} - неправильное. Еще раз.')

                    our_cur = input(f'Выбирете валюту рубл. / доллар (нажмите r / d): ')

                    if our_cur == 'r' or our_cur == 'd':

                        break

                    # our_cur = input(f'Выбирете валюту рубл. / доллар (нажмите r / d): ')

                user_pay.append(our_cur)
                user_pay.append(int(our_pay))

            break


        except ValueError as error:

            print(f'\nПроизошла ошибка: {str(error)[0:37]}.')
            our_pay = input(f'Введите начальное значение ЗП в выбранной валюте (еще раз): ')

            continue


# Создается локальная функция которая создает запрос на страницу центро банка, извлекает из нее курс руб/доллар
# и запрашивает у БД вакансии с ЗП соответствующе запросу пользователя как в рублях, так и в долларах

    def show_pay(currency, pay):

# Создание запроса на страницу центробанка

        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
            'Accept': '*/*'}

        link_currency = 'https://cbr.ru/'

        response = r.get(link_currency, headers=header).text

        soup = bs(response, 'lxml')

        block = soup.find('tbody')

# Обработка курса валют на странице центробанка

        today_currency = float(
            block.findChildren(recursive=False)[1].find_all('div', {'class': 'value'})[1].getText()[:-1].replace(',', '.'))

# Открывается условие, в котором создается локальная переменная, которая содержит размер зарплаты в валюте
# отдичной от введеной пользователем

        if currency == 'd':

            pay_rubl = float(pay) * today_currency

            i = 0

# Выполняется запрос к БД, который потребует, чтобы вакансия содержала сведения о валюте и соответствовала
# требованию начальной зарплаты

            for vacancy in vacancies_db.find({'$or': [
                {'$and': [{'Валюта': {'$eq': 'USD'}, 'Зарплата (от)': {'$ne': 'null', '$gte': pay}}]},
                {'$and': [{'Валюта': {'$eq': 'руб.'}, 'Зарплата (от)': {'$ne': 'null', '$gte': pay_rubl}}]}]}):

                i += 1

                pprint(vacancy)
                print('\n')

            print(f'\n\nКоличество найденных вакансий: {i}')


        elif currency == 'r':

            pay_dollar = float(pay) / today_currency

            i = 0

            for vacancy in vacancies_db.find({'$or': [
                {'$and': [{'Валюта': {'$eq': 'USD'}, 'Зарплата (от)': {'$ne': 'null', '$gte': pay_dollar}}]},
                {'$and': [{'Валюта': {'$eq': 'руб.'}, 'Зарплата (от)': {'$ne': 'null', '$gte': pay}}]}]}):

                i += 1

                pprint(vacancy)
                print('\n')

            print(f'\n\nКоличество найденных вакансий: {i}')
        #
        #
        # else:
        #
        #     print(f'Введино неправильное значение валюты')

# Показать результат запроса

    show_pay(*user_pay)


# Готовая функция

# values_for_func()



