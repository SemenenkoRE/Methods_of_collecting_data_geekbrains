from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from pymongo import MongoClient
from lxml import html
from pprint import pprint
import hashlib
import time as t


# Для настройки браузера, создаем объект chrome_options класса Options(). Далее передаем объекту следующие настройки:
# открываться в полноэкранном режиме и режиме, когда мы не можем наблюдать за действиями в браузере

chrome_options = Options()
chrome_options.add_argument('start-maximized')
chrome_options.add_argument('--headless')

# Создание объекта класса webdriver, передаем ему параметры объекта chrome_options

driver = webdriver.Chrome('./chromedriver.exe', options=chrome_options)


# Передаем объекту driver ссылку на почтовый ящик

driver.get('https://mail.ru/?from=logout')


# Создаем базу данных Mongodb, которая будет содержать информацию о письмах на почтовом ящике

client = MongoClient('localhost', 27017)
db = client['mail']
mail = db.mail


# Создаем словарь, который будет содержать необходимую информацию о письмах.
# Словарь в дальнейшем будет передаваться базе данных для ее заполнения

dict_user = {}


# Создаем переменную содержащий список, который пополняется _id уже имеющейся базы данных mail на случай обновления информации

list_id = []

for el in mail.find({}):

    list_id.append(el['_id'])


# Создаем объект element объекта driver, который будет содержать блок с передаваемыми данными о владельце ящика
# Передаем название почтового ящика в соответствующее поля ввода и передаем браузеру команду ENTER

element = driver.find_element_by_id('mailbox:login')
element.send_keys('study.ai_172@mail.ru')
element.send_keys(Keys.ENTER)


# Осуществляем задержку на время обновления страницы

t.sleep(0.5)


# Создаем объект element объекта driver, который будет содержать блок с передаваемым паролем владельца ящика
# Передаем пароль в соответствующее поля ввода и передаем браузеру команду ENTER

element = driver.find_element_by_id('mailbox:password')
element.send_keys('NextPassword172')
element.send_keys(Keys.ENTER)


# Создаем объект element объекта driver, который будет содержать блок посчтового ящика с письмами

t.sleep(5)
element = driver.find_element_by_xpath("//div[@class='dataset-letters']")


# Создаем функцию, которая будет обрабатывать время получения письма в формат 00:00 00:00:0000

def func_get_time(time_):


    # Обработка получаемой информации о дате и времени письма на случай, когда письмо получено ни сегодня или вчера,
    # а также не в прежние года

    if ('2019' and '2018') not in time_ and 'Сегодня' not in time_ and 'Вчера' not in time_:


        # разделяем получаемую инфомацию на переменные даты, месяца, времени

        day, month, hour_sec = time_.split(' ')[0], time_.split(' ')[1][:-1], time_.split(' ')[2]


        # Создаем словарь для дальнейшей обработки информации о месяце

        dict_monthes = {'01': 'января', '02': 'февраля', '03': 'марта', '04': 'апреля', '05': 'мая', '06': 'июня',
                        '07': 'июля', '08': 'августа', '09': 'сентября', '10': 'октября', '11': 'ноября', '12': 'декабря'}


        # Создаем цикл, в котором идентифицируется месяц, переводится в его порядковый номер

        for n, l in dict_monthes.items():


            if l == month:

                month = n


        # Вся ранее извлеченная и обработанная информация переводится в соответствующий вид даты

        time_end = f'{hour_sec} {day}.{month}.2020'


        # Словарь, в дальнейшем передаваемый базе данных, обновляется величиной времени

        dict_user.update({'Дата и время': time_end})


    # Обработка получаемой информации о дате и времени письма на случай, когда письмо получено в прежние года

    elif '2019' in time_ or '2018' in time_:


        day, month, year, hour_sec = time_.split(' ')[0], time_.split(' ')[1], time_.split(' ')[2][:4], time_.split(' ')[3]

        dict_monthes = {'01': 'января', '02': 'февраля', '03': 'марта', '04': 'апреля', '05': 'мая', '06': 'июня',
                        '07': 'июля', '08': 'августа', '09': 'сентября', '10': 'октября', '11': 'ноября', '12': 'декабря'}


        for n, l in dict_monthes.items():


            if l == month:

                month = n


        time_end = f'{hour_sec} {day}.{month}.{year}'

        dict_user.update({'Дата и время': time_end})


    # Обработка получаемой информации о дате и времени письма на случай, когда письмо получено сегодня или вчера

    else:

        hour_sec = time_.split(' ')[1]

        today = t.ctime(t.time())

        dict_monthes = {'01': 'Jan', '02': 'Feb', '03': 'Mar', '04': 'Apr', '05': 'May', '06': 'Jun',
                        '07': 'Jul', '08': 'Aug', '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dec'}


        for n, l in dict_monthes.items():


            if l == today.split(' ')[1]:


                if 'Сегодня' in time_:

                    time_end = f"{hour_sec} {today.split(' ')[2]}.{n}.{today.split(' ')[4]}"

                    dict_user.update({'Дата и время': time_end})


                elif 'Вчера' in time_:

                    time_end = f"{hour_sec} {str(int(today.split(' ')[2])-1)}.{n}.{today.split(' ')[4]}"

                    dict_user.update({'Дата и время': time_end})

    # Т.к. получение времени было последней операцией, заполненный данными словарь передается базе данных
    mail.insert_one(dict_user)

    print(dict_user)

# Создается функция по сбору информации

def get_data_of_mail(el_):

    # Создаем переменные, содержащую прямую ссылку на письмо и краткое содержание письма

    ref = el_.get_attribute('href')
    text_of_mail = el_.find_element_by_class_name('ll-sp__normal').text.split(' -- ')[0]

    # Создаем захешированное значение от текста ссылки написьмо и его краткого содержимого
    # Далее создаем переменную id, которая будет содержать полученное захешированное значение, и будет явл-ся id в БД

    hash_object = hashlib.sha1(bytes((ref+text_of_mail), encoding='utf-8'))
    hex_dig = hash_object.hexdigest()

    id = hex_dig


    # Создается отработка исключения, на тот случай если что то пойдет не так, но проверка показала, что такие
    # прициденты должны отсутствовать

    try:

        if id not in list_id:

            # Т.к. объявление прошло проверку на отсутствие такого id в БД, новый id добавляется в список list_id

            list_id.append(id)


            # Создаем переменные name_from (имя отправителя), mail_from (почта отправителя), subject_of_mail (тема письма)
            # time_init (необработанное время получения письма), которые получают информацию со страницы почты и
            # обрабатывает ее в необходимый вид

            name_from = el_.find_element_by_class_name('ll-crpt').text

            mail_from = el_.find_element_by_class_name('ll-crpt').get_attribute('title')[
                        el_.find_element_by_class_name('ll-crpt').get_attribute('title').index('<')+1
                        :el_.find_element_by_class_name('ll-crpt').get_attribute('title').index('>')]

            subject_of_mail = el_.find_element_by_class_name('ll-sj__normal').text

            time_init = el_.find_element_by_class_name('llc__item_date').get_attribute('title')


            # Обновляем словарь с содержимым писем

            dict_user.update(
                {'_id': id, 'Ссылка': ref, 'Имя отправителя': name_from, 'Почта отправителя': mail_from,
                 'Тема письма': subject_of_mail, 'Краткое содержание письма': text_of_mail})


            # Запускаем функцию по обработке времени в необходимый формат

            func_get_time(time_init)

    except Exception as error:

        print(f'Ошибка: {error}')


# Создаем функцию осуществляющая скроллинг в браузере до того письма в блоке с письмами, чтобы последовало
# дальнейшее добавление писем на странице сайта

def scroll_mails(driver_):

    actions = ActionChains(driver_)

    actions.move_to_element(element.find_elements_by_tag_name('a')[-1])

    actions.perform()


# Создаем функцию которая перебирает объекты el из полученного для обработки объектов списка element__
# Для дальнейшего скроллинга до последнего письма из списка писем создается список test_list, который будет указывать
# на индекс последнего объекта в списке имеющихся объектов страниц

def begin_collecting_data_mail(element__):

    try:

        test_list = []

        for el in element__:


            # Условие, выполняемое когда объект с письмом не находится последним в списке объектов

            if el.get_attribute('data-uidl-id') and el != element__[-1]:

                n = str(f'{el}')

                test_list.append(n)

                get_data_of_mail(el)



            # Условие, выполняемое когда объект с письмом находится последним в списке объектов

            elif el.get_attribute('data-uidl-id') and el == element__[-1]:

                n = str(f'{el}')

                test_list.append(n)

                get_data_of_mail(el)

                scroll_mails(driver)

                t.sleep(2)

                element = driver.find_element_by_xpath("//div[@class='dataset-letters']")

                element_ = element.find_elements_by_tag_name('a')[(test_list.index(f'{el}')+1):]

                begin_collecting_data_mail(element_)

    except Exception as error:

        print(f'По причине ошибки: {error}\nПрограмма запускается еще раз')

        element_ = element.find_elements_by_tag_name('a')

        begin_collecting_data_mail(element_)


# В объекте с объектами писем находится подходящий тег для дальнейшего получения и обработки информации

element_ = element.find_elements_by_tag_name('a')


# Запуск функции, начинающая процесс получения и обраюотки информации

begin_collecting_data_mail(element_)

