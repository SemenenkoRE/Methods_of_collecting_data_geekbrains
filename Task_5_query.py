import requests as r
from pprint import pprint
from lxml import html
import time
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client['mail']

mail = db.mail

# for n in mail.find({}):
#
#     pprint(n)


mail.delete_many({})