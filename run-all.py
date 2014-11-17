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

client = MongoClient('127.0.0.1', 27017)
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


def zulip_watch_all():
    readers = []
    for user in users.find():
        print 'USER', user['zulip_key'], user['zulip_email']
        message_reader = MessageReader(user['zulip_email'], user['zulip_key'])
        message_reader.start()
        readers.append(message_reader)

    return readers


# This is a blocking call, and will continuously poll for new messages
if __name__ == '__main__':
    monkey.patch_all(aggressive=False)
    readers = zulip_watch_all()

    flask_app.run_app()

    # Wait for all the readers to finish (should be never)
    for reader in readers:
        reader.join()

