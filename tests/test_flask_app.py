import zuliptree.flask_app as flask_app
def test_blah():
    assert(True)

def test_get_zulip_pointer(monkeypatch):
    monkeypatch.setenv('DEBUG', 'True')
    assert(flask_app.get_zulip_pointer() == 100)

def test_get_zulip_subscriptions():
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
