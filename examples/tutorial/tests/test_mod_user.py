import pytest

from flaskr.db import get_db

def test_update(client, auth, app):
    auth.login()
    assert client.get("/updateEmail").status_code == 200
    client.post("/updateEmail", data={"email": "NA@NA"})

    with app.app_context():
        db = get_db()
        post = db.execute("SELECT * FROM user WHERE id = 1").fetchone()
        assert post["email"] == "updated"