import pymongo
import random
from pymongo import MongoClient
import json
from bson.json_util import dumps
import requests
import pprint



client = MongoClient('104.131.112.57', 49158)
db = client.zulipTree

# TODO have the two requests concurrent
pointer_req = requests.get('https://api.zulip.com/v1/users/me/pointer',
                        auth=requests.auth.HTTPBasicAuth('chaselambda@gmail.com',
                                                         'L82nGQwwWneF0s9iqkGPqJDgmvmZVDu1'),
                        verify=True)


subscriptions_req = requests.get('https://api.zulip.com/v1/users/me/subscriptions',
                        auth=requests.auth.HTTPBasicAuth('chaselambda@gmail.com',
                                                         'L82nGQwwWneF0s9iqkGPqJDgmvmZVDu1'),
                        verify=True)
# TODO error checking..
pointer = int(pointer_req.json()['pointer'])

subscriptions = {}
for subscription in subscriptions_req.json()['subscriptions']:
    subscriptions[subscription['name']] = subscription['in_home_view']

print 'pointer is', pointer

def visible_message(message):
    if type(message['display_recipient']) in [str, unicode]:
        return subscriptions[message['display_recipient']]
    else:
        assert(type(message['display_recipient']) is list)
        assert(message['type'] == 'private')

streams = {}
messages = db['messages']
for message in messages.find({'id': {'$gt': pointer}}):
    #print dumps(message, sort_keys=True, indent=4, separators=(',', ': '))
    if len(message['subject_links']) > 0:
        print 'NOTICE: Message has some subject links:'
        print dumps(message, sort_keys=True, indent=4, separators=(',', ': '))

    if visible_message(message):
        stream = message['display_recipient']
        if stream not in streams:
            streams[stream] = []
        streams[stream].append(message['subject'])

for stream, subjects in streams.iteritems():
    assert(stream in subscriptions)
    streams[stream] = list(set(subjects))

print json.dumps(streams, sort_keys=True, indent=4, separators=(',', ': '))
