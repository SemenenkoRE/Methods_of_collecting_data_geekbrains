import requests as r
from pprint import pprint
from lxml import html
import time
from pymongo import MongoClient
import hashlib


# Создаем MongoClient

client = MongoClient('localhost', 27017)
db = client['news']


# Создаем базу данных, в которую будут входить новости из трех источников:
# https://lenta.ru/, https://news.mail.ru/, https://yandex.ru

news = db.news


header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36', 'Accept': '*/*'}


# Создаем переменную содержащий список, который пополняется _id уже имеющейся базы данных news

list_id = []

for el in news.find({}):

    list_id.append(el['_id'])


dict_user = {}


# Создаем функцию, которая будет для всех источников добавлять в базу данных готовый словарь с данными

def add_to_bd(object_add):

    news.insert_one(object_add)


# Создаем функцию, которая будет для всех источников хешировать передаваемую ей строковую информацию (описание новости)
# и передает ссловорю с данными данный хеш в качестве значения _id


def make_uniq_id(uniq_expr):

    hash_object = hashlib.sha1(bytes(uniq_expr, encoding = 'utf-8'))
    hex_dig = hash_object.hexdigest()
    dict_user.update({'_id': hex_dig})

    add_to_bd(dict_user)


# Создаем функцию, которая обрабатывать время со страницы новости

def func_get_time_lenta(_block):

    time_hours = _block.xpath(".//time[@class='g-time']/text()")[0]

    time_days = _block.xpath(".//time[@class='g-time']/@title")[0]

    dict_monthes = {'01': 'января', '02': 'февраля', '03': 'марта', '04': 'апреля', '05': 'мая', '06': 'июня',
                    '07': 'июля', '08': 'августа', '09': 'сентября', '10': 'октября', '11': 'ноября', '12': 'декабря'}


    for n, l in dict_monthes.items():

        if l == time_days.split(' ')[1]:

            time_news = f"{time_hours} {time_days.split(' ')[0]}.{n}.{time_days.split(' ')[2]}"

            dict_user.update({'Время новости': time_news})

    make_uniq_id(dict_user['Описание новости'])


# Создаем функцию, которая заходит на страницу с новостями. Т.к. блок новостей состояит из двух блоков, проходит по
# по каждому из них и извлекает описание новости, ссылку на новость. Также проверяет на повторение новости в имеющейся
# базе данных, в таковом случае пропускает дальнейший код. Если таковой новости не было, то пополняет значениями
# словарь, передаваемый в дальнейшем базе данных.

def func_get_values_lenta(object_dom):

    for el in object_dom:

        for el_ in el:

            if el_.xpath(".//time[@class='g-time']"):

                news_text = el_.xpath(".//a/text()")[0].replace('\xa0', ' ')
                source = 'lenta.ru'

                hash_object = hashlib.sha1(bytes(news_text, encoding='utf-8'))
                hex_dig = hash_object.hexdigest()

                if hex_dig in list_id:

                    continue

                ref = 'https://lenta.ru/' + el_.xpath(".//a/@href")[0]
                dict_user.update({'Описание новости': news_text, 'Ссылка': ref, 'Источник': source})

                func_get_time_lenta(el_)


# Функция позволяет заходить на страницу с новостями источника

def func_get_response_lenta():

    response = r.get('https://lenta.ru/', headers=header)

    dom = html.fromstring(response.text)

    func_get_values_lenta(dom.xpath("//section[@class='row b-top7-for-main js-top-seven']/div"))


# Создаем функцию, которая обрабатывать время со страницы новости

def func_get_time_yandex():

    time_news = time.ctime(time.time())

    dict_monthes = {'01': 'Jan', '02': 'Feb', '03': 'Mar', '04': 'Apr', '05': 'May', '06': 'Jun',
                    '07': 'Jul', '08': 'Aug', '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dec'}

    for n, l in dict_monthes.items():

        if l in time_news:

            time_news = f"{time_news.split(' ')[3][0:5]} {time_news.split(' ')[2]}.{n}.{time_news.split(' ')[4]}"

            dict_user.update({'Время новости': time_news})

    make_uniq_id(dict_user['Описание новости'])


# Т.к. источник новости внутри страницы с новостью, функция переходит по ссылке внутрь и обрабатывает текст с источником

def func_get_sours_yandex(ref_in):

    response = r.get(ref_in, headers=header)

    dom_ = html.fromstring(response.text)

    sours = dom_.xpath(".//span[@class='story__head-agency']//a/text()")[0]

    dict_user.update({'Источник': sours})

    func_get_time_yandex()


# Создаем функцию, которая заходит на страницу с новостями. Проходит по по каждому из блоков с новостями и извлекает
# описание новости, ссылку на новость. Также проверяет на повторение новости в имеющейся базе данных,
# в таковом случае пропускает дальнейший код. Если таковой новости не было, то пополняет значениями
# словарь, передаваемый в дальнейшем базе данных.

def func_get_values_yandex(object_dom):

    for el in object_dom:

        news_text = el.xpath(".//a/text()")[0].replace('&nbsp;', ' ')

        hash_object = hashlib.sha1(bytes(news_text, encoding='utf-8'))

        hex_dig = hash_object.hexdigest()

        if hex_dig in list_id:

            continue

        ref = 'https://yandex.ru' + el.xpath(".//a/@href")[0]

        dict_user.update({'Описание новости': news_text, 'Ссылка': ref})

        func_get_sours_yandex(ref)


# Функция позволяет заходить на страницу с новостями источника

def func_get_response_yandex():

    response = r.get('https://yandex.ru/news/', headers=header)

    dom = html.fromstring(response.text)

    func_get_values_yandex(
        dom.xpath("//div[@class='stories-set stories-set_main_no stories-set_pos_1']//td[@class='stories-set__item']"))


# Создаем функцию, которая передавать переменной time (время новости) текущее время, т.к. времени на странице сайта нет

def func_mod_time_mail(user_time):

    time_date = user_time[:10]

    time_hour = user_time[11:16]

    time = f"{time_hour} {time_date.split('-')[2]}.{time_date.split('-')[1]}.{time_date.split('-')[0]}"

    dict_user.update({'Время новости': time})

    make_uniq_id(dict_user['Описание новости'])


# Т.к. источник новости внутри страницы с новостью, функция переходит по ссылке внутрь и обрабатывает текст с источником.
# Т.к. если источник отсутствует, на странице сайта источник заполняется как 'Новости Mail.ru'. Поэтому при отсутствии
# новости источником становится Новости Mail.ru'

def func_get_sours_time_mail(ref_in):

    response_ = r.get(ref_in, headers=header)

    dom_ = html.fromstring(response_.text)

    sours = dom_.xpath("//div[@name='clb20266164']//span[@class='link__text']/text()")

    if not sours:

        sours = 'Новости Mail.ru'

    else:

        sours = dom_.xpath("//div[@name='clb20266164']//span[@class='link__text']/text()")[0]

    time = dom_.xpath("//div[@name='clb20266164']//span[@class='note__text breadcrumbs__text js-ago']/@datetime")[0]

    dict_user.update({'Источник': sours})

    func_mod_time_mail(time)


# Создаем функцию, которая заходит на страницу с новостями. Проходит по по каждому из блоков с новостями и извлекает
# описание новости, ссылку на новость. Также проверяет на повторение новости в имеющейся базе данных,
# в таковом случае пропускает дальнейший код. Если таковой новости не было, то пополняет значениями
# словарь, передаваемый в дальнейшем базе данных.

def func_get_values_mail(object_dom):

    for el in object_dom:

        news_text = el.xpath(".//a[@class='list__text']/text()")[0].replace('\xa0', ' ')

        hash_object = hashlib.sha1(bytes(news_text, encoding='utf-8'))

        hex_dig = hash_object.hexdigest()

        if hex_dig in list_id:

            continue

        if el.xpath(".//a[@class='list__text']/@href")[0][0:5] == 'https':

            continue

        else:

            ref = f'https://news.mail.ru/' + el.xpath(".//a[@class='list__text']/@href")[0]  #####

        dict_user.update({'Описание новости': news_text, 'Ссылка': ref})

        func_get_sours_time_mail(ref)


# Функция позволяет заходить на страницу с новостями источника

def func_get_response_mail():

    response = r.get('https://news.mail.ru/', headers=header)

    dom = html.fromstring(response.text)

    func_get_values_mail(dom.xpath("//div[@class='block']//li"))


# Исполнение написанных ранее функций по сбору данных с новостями

func_get_response_lenta()
func_get_response_yandex()
func_get_response_mail()