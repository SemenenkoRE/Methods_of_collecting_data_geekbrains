import requests as r
from pprint import pprint
from lxml import html
import time
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client['news']

news = db.news

for n in news.find({}):

    pprint(n)


# news.delete_many({})
