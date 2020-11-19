from .conftest import test_client

def test_guest(test_client):
    resp = test_client.get("/")
    assert resp.status_code == 200
    assert resp.data == b"hello Guest"

def test_user(test_client):
    resp = test_client.get("/whoami")
    assert resp.status_code == 403


    resp = test_client.get("/", headers={"user": "alice@foo.com"})
    assert resp.status_code == 200
    assert resp.data.decode().startswith("hello User")

    resp = test_client.get("/whoami", headers={"user": "alice@foo.com"})
    assert resp.status_code == 200
    assert resp.data.decode().startswith("You are alice@foo.com")

    resp = test_client.get("/expenses/1", headers={"user": "alice@foo.com"})
    assert resp.status_code == 403

    resp = test_client.get("/expenses/2", headers={"user": "alice@foo.com"})
    assert resp.status_code == 200
    assert resp.json["id"] == 2

    

