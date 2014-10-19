#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import optparse
import random
import gevent
from pymongo import MongoClient

client = MongoClient('104.131.112.57', 49158)
db = client.zulipTree
messages = db['messages']


usage = """message-watch --user=<bot's email address> --api-key=<bot's api key> [options]

Prints out each message received by the indicated bot or user.

Example: message-watch --user=tabbott@zulip.com --api-key=a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5

You can omit --user and --api-key arguments if you have a properly set up ~/.zuliprc
"""
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import zulip

parser = optparse.OptionParser(usage=usage)
parser.add_option_group(zulip.generate_option_group(parser))
(options, args) = parser.parse_args()


class MessageReader(gevent.Greenlet):
    def __init__(self):
        gevent.Greenlet.__init__(self)

    def _run(self):
        client = zulip.init_from_options(options)
        print 'Reading messags'
        client.call_on_each_message(print_message)

def print_message(message):
    print 'Someone said: ', message['content']
    print 'Inserting Message:', message
    messages.insert(message)

# This is a blocking call, and will continuously poll for new messages
if __name__ == '__main__':
    message_reader = MessageReader()
    message_reader.start()
    message_reader.join() # take out later
    #runner = FlaskRunner()
    #runner.start()
    #runner.join()


    
