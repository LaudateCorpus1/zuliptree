import pymongo
import random
from pymongo import MongoClient

client = MongoClient('104.131.112.57', 49158)
db = client.zulipTree
messages = db['messages']
for message in messages.find():
    print message

rand_str = str(int(random.random() * 1000))
new_messages = [{'name': 'chase', 'message': 'another one ' + rand_str}]
messages.insert(new_messages)
