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

class MessageReader(gevent.Greenlet):
    def __init__(self):
        gevent.Greenlet.__init__(self)

    def _run(self):
        print 'run reader'
        zulip_watch.zulip_watch('chaselambda@gmail.com', 'L82nGQwwWneF0s9iqkGPqJDgmvmZVDu1')

def print_message(message):
    print 'Someone said: ', message['content']
    print 'Inserting Message:', message
    messages.insert(message)

# This is a blocking call, and will continuously poll for new messages
if __name__ == '__main__':
    monkey.patch_all(aggressive=False)
    message_reader = MessageReader()
    message_reader.start()

    flask_app.run_app()
    message_reader.join()

