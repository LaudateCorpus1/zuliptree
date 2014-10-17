import pymongo
import random
from pymongo import MongoClient

client = MongoClient('104.131.112.57', 49158)
db = client.zulipTree
messages = db['messages']
for message in messages.find({'id': {'$gt': 29275000}}):
    print message

