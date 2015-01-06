from .. import zulip
from .. import run_all
import pytest
import gevent
import zuliptree.flask_app as flask_app
def test_blah():
    assert(True)

def test_get_zulip_pointer(monkeypatch):
    monkeypatch.setenv('DEBUG', 'True')
    assert(flask_app.get_zulip_pointer() == 100)

def test_get_zulip_subscriptions(monkeypatch):
    monkeypatch.setenv('DEBUG', 'True')
    assert('checkins' in flask_app.get_zulip_subscriptions())

def test_visible_message():
    subscriptions = {'checkins': True, 'programming': True} 

    message = {'display_recipient': [], 'type': 'private'}
    assert(not flask_app.visible_message(subscriptions, message))

    message = {'display_recipient': 'nothing'}
    assert(not flask_app.visible_message(subscriptions, message))

    message = {'display_recipient': 'checkins'}
    assert(flask_app.visible_message(subscriptions, message))

    message = {'display_recipient': u'checkins'}
    assert(flask_app.visible_message(subscriptions, message))

    message = {}
    assert(not flask_app.visible_message(subscriptions, message))

class FailFirstClosure:
    def __init__(self):
        self.counter = 0
    def __call__(self, *args, **kwargs):
        if self.counter == 0:
            self.counter += 1
            raise Exception("I just blew up")
        self.counter += 1

def test_closure():
    call_on_each_message = FailFirstClosure()

    with pytest.raises(Exception):
        call_on_each_message()
    call_on_each_message()
    assert(call_on_each_message.counter == 2)

def test_dead_watcher(monkeypatch):
    monkeypatch.setenv('DEBUG', 'True')
    print 'test dead'
    call_on_each_message = FailFirstClosure()
    def noop_fn(*args, **kwargs):
        return None
    monkeypatch.setattr(zulip.Client, '__init__', noop_fn)
    monkeypatch.setattr(zulip.Client, 'call_on_each_message', call_on_each_message)

    ## start up watcher
    message_reader = run_all.MessageReader('email@email.com', 'my key')
    message_reader.start()
    message_reader.join()

    # Check that our MessageReader restarted.
    assert(call_on_each_message.counter == 2)

