from flask import Flask, render_template
import pymongo
import random
from pymongo import MongoClient
import json
from bson.json_util import dumps
import requests
import pprint

client = MongoClient('104.131.112.57', 49158)
db = client.zulipTree
app = Flask(__name__)
DEBUG = False

def get_zulip_pointer():
    # TODO error checking..
    # TODO have the two requests concurrent
    if DEBUG:
        return 100
    pointer_req = requests.get('https://api.zulip.com/v1/users/me/pointer',
                            auth=requests.auth.HTTPBasicAuth('chaselambda@gmail.com',
                                                             'L82nGQwwWneF0s9iqkGPqJDgmvmZVDu1'),
                            verify=True)
    return int(pointer_req.json()['pointer'])

def get_zulip_subscriptions():
    if DEBUG:
        return {'checkins': True, 'programming': True}
    subscriptions_req = requests.get('https://api.zulip.com/v1/users/me/subscriptions',
                            auth=requests.auth.HTTPBasicAuth('chaselambda@gmail.com',
                                                             'L82nGQwwWneF0s9iqkGPqJDgmvmZVDu1'),
                            verify=True)

    subscriptions = {}
    for subscription in subscriptions_req.json()['subscriptions']:
        subscriptions[subscription['name']] = subscription['in_home_view']
    return subscriptions

def visible_message(subscriptions, message):
    stream = message['display_recipient']
    if type(stream) in [str, unicode]:
        return stream in subscriptions and subscriptions[stream]
    else:
        assert(type(stream) is list)
        assert(message['type'] == 'private')

def get_zulip_tree():
    pointer = get_zulip_pointer()
    subscriptions = get_zulip_subscriptions()
    print 'pointer is', pointer

    streams = {}
    if DEBUG:
        streams['checkins'] = ['Russell']
        streams['programming'] = ['Russell']

    messages = db['messages']
    for message in messages.find({'id': {'$gt': pointer}}):
        #print dumps(message, sort_keys=True, indent=4, separators=(',', ': '))
        if len(message['subject_links']) > 0:
            print 'NOTICE: Message has some subject links:'
            print dumps(message, sort_keys=True, indent=4, separators=(',', ': '))

        if visible_message(subscriptions, message):
            stream = message['display_recipient']
            if stream not in streams:
                streams[stream] = []
            streams[stream].append(message['subject'])

    for stream, subjects in streams.iteritems():
        assert(stream in subscriptions)
        streams[stream] = list(set(subjects))

    #return json.dumps(streams, sort_keys=True, indent=4, separators=(',', ': '))
    return render_template('index.html', streams=streams)

def get_google():
    req = requests.get('http://google.com')
    return str(req.status_code)


@app.route('/')
def hello_world():
    return get_zulip_tree()

def run_app():
    print 'Starting flask app'
    app.run('0.0.0.0', debug=True)


if __name__ == '__main__':
    run_app()
