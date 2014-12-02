from flask import Flask, render_template, request, session, redirect, url_for
import pymongo
import random
from pymongo import MongoClient
import json
from bson.json_util import dumps
import requests
import pprint
import os
import urllib
from collections import defaultdict

with open('mongo-pass.conf', 'r') as f:
    mpass = f.read().strip()
    client = MongoClient('mongodb://chase:{}@104.131.112.57'.format(mpass))
db = client.zulipTree
users = db['users']

app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!kalsdjkas#$$$@#$T'

DEBUG = 'DEBUG' in os.environ and os.environ['DEBUG'] == 'True'
debug_streams = {'checkins': {'Russell': ['bob']},
        'code review': {'Ping me if you want code review/pairing': ['Peter Seibel']}}

def streams_to_subscriptions(streams):
    ret= {}
    for stream, l in streams.iteritems():
        ret[stream] = True
    return ret

@app.template_filter('urlencode2')
def urlencode2(s):
    return urllib.quote(s.encode('utf8'), safe='')

def get_zulip_pointer():
    # TODO error checking..
    # TODO have the two requests concurrent
    if DEBUG:
        return 100

    return get_zulip_pointer_nosession(session['email'], session['key'])

def get_zulip_pointer_nosession(email, key):
    pointer_req = requests.get('https://api.zulip.com/v1/users/me/pointer',auth=requests.auth.HTTPBasicAuth(email, key),verify=True)
    return int(pointer_req.json()['pointer'])


def get_zulip_subscriptions():
    if DEBUG:
        return streams_to_subscriptions(debug_streams)
    subscriptions_req = requests.get('https://api.zulip.com/v1/users/me/subscriptions',
                            auth=requests.auth.HTTPBasicAuth(session['email'],
                                                             session['key']),
                            verify=True)

    subscriptions = {}
    for subscription in subscriptions_req.json()['subscriptions']:
        subscriptions[subscription['name']] = subscription['in_home_view']
    return subscriptions

def visible_message(subscriptions, message):
    try:
        stream = message['display_recipient']
        if type(stream) in [str, unicode]:
            return subscriptions[stream]
        else:
            assert(type(stream) is list)
            assert(message['type'] == 'private')
    except KeyError:
        return False

def get_zulip_tree():
    pointer = get_zulip_pointer()
    subscriptions = get_zulip_subscriptions()
    print 'pointer is', pointer

    streams = defaultdict(lambda: defaultdict(list))
    if DEBUG:
        streams = debug_streams

    messages = db['messages']
    for message in messages.find({'id': {'$gt': pointer}, 'watcher_email': session['email']}):
        #print dumps(message, sort_keys=True, indent=4, separators=(',', ': '))
        if len(message['subject_links']) > 0:
            # TODO log error?
            print 'NOTICE: Message has some subject links:'
            print dumps(message, sort_keys=True, indent=4, separators=(',', ': '))

        if visible_message(subscriptions, message):
            stream = message['display_recipient']
            streams[stream][message['subject']].append(message['sender_full_name'])

    for stream, topics in streams.iteritems():
        assert(stream in subscriptions)
        for topic, authors in topics.iteritems():
            topics[topic] = list(set(authors))

    #return json.dumps(streams, sort_keys=True, indent=4, separators=(',', ': '))
    return render_template('index.html', streams=streams, no_streams=len(streams) == 0)

def get_google():
    req = requests.get('http://google.com')
    return str(req.status_code)


@app.route('/')
def hello_world():
    if 'email' not in session:
        return redirect(url_for('login'))
    return get_zulip_tree()

@app.route('/blah')
def blah():
    return 'hello there, this is blah'

@app.route('/logout')
def logout():
    session.pop('email', None)
    return 'Logged out! <a href="/login">Login</a>'

@app.route('/login', methods=['GET'])
@app.route('/login')
def login():
    if 'email' in session:
        return 'You already are logged in as {} :).. <a href="/logout">Logout</a>'.format(session['email'])
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    found_user = users.find({'zulip_email': request.form['zulip_email']})
    if found_user.count() > 0:
        # Set the users session
        session['email'] = request.form['zulip_email']
        session['key'] = found_user[0]['zulip_key']
        print 'Key saved', session['key']

        return redirect('/')
    user = {}
    user['zulip_key'] = request.form['zulip_key']
    user['zulip_email'] = request.form['zulip_email']

    try:
        pointer = get_zulip_pointer_nosession(user['zulip_email'], user['zulip_key'])
    except Exception as e:
        return 'Your login did not seem to work.. try <a href="/login">Logging in</a> again?'

    session['email'] = request.form['zulip_email']
    session['key'] = user['zulip_key']

    users.insert(user)
    return redirect('/')


def run_app():
    print 'Starting flask app'
    app.run('0.0.0.0', debug=True)


if __name__ == '__main__':
    run_app()
