#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import optparse
import random
import zulip
import conf
import logging
import time
import pymongo
import gevent

client = conf.get_db_client()
db = client.zulipTree
messages = db['messages']
users = db['users']
def is_debug():
    return 'DEBUG' in os.environ and os.environ['DEBUG'] == 'True'

# oh hey there

# def main():
#     usage = """message-watch --user=<bot's email address> --api-key=<bot's api key> [options]

#     Prints out each message received by the indicated bot or user.

#     Example: message-watch --user=tabbott@zulip.com --api-key=a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5

#     You can omit --user and --api-key arguments if you have a properly set up ~/.zuliprc
#     """

#     parser = optparse.OptionParser(usage=usage)
#     parser.add_option_group(zulip.generate_option_group(parser))
#     (options, args) = parser.parse_args()

#     client = zulip.init_from_options(options)

def print_message_wrapper(email):
    def print_message(message):
        print 'Someone said: ', message['content'].encode('utf-8')
        print 'Inserting Message:', message
        message['watcher_email'] = email
        messages.insert(message)
    return print_message

def zulip_watch(email, api_key):
    while True:
        try:
            print("Starting (or restarting) watcher for {}".format(email))
            client = zulip.Client(email=email, api_key=api_key, config_file=None,
                          verbose=False, site=None, client='API: Python')
            client.call_on_each_message(print_message_wrapper(email))
            if is_debug():
                return 0
        except:
            logging.exception("zulip_watch failed. Sleeping for a bit before restarting.")
            if not is_debug():
                time.sleep(5)



# This is a blocking call, and will continuously poll for new messages
if __name__ == '__main__':
    print 'Do not run this file...'
