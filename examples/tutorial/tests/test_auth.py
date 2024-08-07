import pytest
from flask import g
from flask import session

from flaskr.db import get_db


def test_register(client, app):
    # test that viewing the page renders without template errors
    assert client.get("/auth/register").status_code == 200

    # test that successful registration redirects to the login page
    response = client.post("/auth/register", data={"username": "a", "password": "a", "email": "a"})
    assert response.headers["Location"] == "/auth/login"

    # test that the user was inserted into the database
    with app.app_context():
        assert (
            get_db().execute("SELECT * FROM user WHERE username = 'a'").fetchone()
            is not None
        )


@pytest.mark.parametrize(
    ("username", "password", "email", "message"),
    (
        ("", "a", "a@test", "Se requiere un usuario."),
        ("a", "", "a@test", "Se requiere una contraseña."),
        ("a", "a", "", "Se requiere un email."),
        ("test", "test", "a@test", "El usuario test ya esta registrado."),
        ("abd", "test", "afswh@a@", "El email afswh@a@ ya esta registrado."),
    ),
)
def test_register_validate_input(client, username, password, email, message):
    response = client.post(
        "/auth/register", data={"username": username, "password": password, "email": email}
    )
    assert message in response.data.decode()


def test_login(client, auth):
    # test that viewing the page renders without template errors
    assert client.get("/auth/login").status_code == 200

    # test that successful login redirects to the index page
    response = auth.login()
    assert response.headers["Location"] == "/"

    # login request set the user_id in the session
    # check that the user is loaded from the session
    with client:
        client.get("/")
        assert session["user_id"] == 1
        assert g.user["username"] == "test"


@pytest.mark.parametrize(
    ("username", "password", "message"),
    (("a", "test", "El usuario o contraseña es incorrecto."), ("test", "a", "El usuario o contraseña es incorrecto.")),
)
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    assert message in response.data.decode()                            


def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert "user_id" not in session
