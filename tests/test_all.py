import zuliptree.flask_app as flask_app
def test_blah():
    assert(True)

def test_get_zulip_pointer(monkeypatch):
    monkeypatch.setenv('DEBUG', 'True')
    assert(flask_app.get_zulip_pointer() == 100)

