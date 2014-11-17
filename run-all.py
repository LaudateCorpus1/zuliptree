#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import optparse
import random
import gevent
from gevent import monkey
from pymongo import MongoClient
import flask_app
import zulip_watch
import time

client = MongoClient('104.131.112.57', 49158)
db = client.zulipTree
users = db['users']

class MessageReader(gevent.Greenlet):
    def __init__(self, email, key):
        self.email = email
        self.key = key
        gevent.Greenlet.__init__(self)

    def _run(self):
        print 'RUN reader: ', self.email, self.key
        # TODO get rid of this key.. and revoke the key
        zulip_watch.zulip_watch(self.email, self.key)

class NewUserPoller(gevent.Greenlet):
    def __init__(self):
        gevent.Greenlet.__init__(self)

    def _run(self):
        print 'RUN NewUserPoller'
        current_emails = []
        while True:
            time.sleep(5)
            current_emails = poll_new_users(current_emails)

def poll_new_users(current_emails):
    return_emails = list(current_emails)

    for user in users.find():
        if user['zulip_email'] not in return_emails:
            print 'NEW USER', user['zulip_key'], user['zulip_email']
            message_reader = MessageReader(user['zulip_email'], user['zulip_key'])
            message_reader.start()

            return_emails.append(user['zulip_email'])
    return return_emails

# This is a blocking call, and will continuously poll for new messages
if __name__ == '__main__':
    monkey.patch_all(aggressive=False)

    newUserPoller = NewUserPoller()
    newUserPoller.start()

    flask_app.run_app()
