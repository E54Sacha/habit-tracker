from datetime import UTC, datetime, timedelta

import jwt
from sqlalchemy import select

from app.config import get_settings
from app.db import SessionLocal
from app.models import User
from app.security import COOKIE_NAME, create_token

PASSWORD = "correct horse battery"


def signup(client, email="ada@example.com", password=PASSWORD):
    return client.post("/auth/signup", json={"email": email, "password": password})


def test_signup_logs_you_in(client):
    response = signup(client)
    assert response.status_code == 201
    assert response.json()["email"] == "ada@example.com"
    assert client.get("/auth/me").json()["email"] == "ada@example.com"


def test_session_cookie_is_protected(client):
    cookie = signup(client).headers["set-cookie"].lower()
    assert f"{COOKIE_NAME}=" in cookie
    assert "httponly" in cookie
    assert "samesite=lax" in cookie
    assert "max-age=604800" in cookie  # 7 days


def test_password_is_hashed_with_argon2(client):
    signup(client)
    with SessionLocal() as db:
        user = db.scalar(select(User))
    assert PASSWORD not in user.password_hash
    assert user.password_hash.startswith("$argon2id$")


def test_email_is_case_insensitive(client, make_client):
    signup(client, email="Ada@Example.com")
    assert signup(make_client(), email="ada@example.COM").status_code == 409
    response = make_client().post("/auth/login", json={"email": "ADA@example.com", "password": PASSWORD})
    assert response.status_code == 200


def test_signup_rejects_bad_input(client):
    assert signup(client, email="not-an-email").status_code == 422
    assert signup(client, password="short").status_code == 422
    assert signup(client, password="x" * 129).status_code == 422


def test_login_and_logout(client, make_client):
    signup(client)
    browser = make_client()
    assert browser.get("/auth/me").status_code == 401
    assert browser.post("/auth/login", json={"email": "ada@example.com", "password": PASSWORD}).status_code == 200
    assert browser.get("/auth/me").status_code == 200
    assert browser.post("/auth/logout").status_code == 204
    assert browser.get("/auth/me").status_code == 401


def test_wrong_email_and_wrong_password_look_the_same(client, make_client):
    signup(client)
    wrong_password = make_client().post("/auth/login", json={"email": "ada@example.com", "password": "nope-nope"})
    wrong_email = make_client().post("/auth/login", json={"email": "bob@example.com", "password": PASSWORD})
    assert wrong_password.status_code == wrong_email.status_code == 401
    assert wrong_password.json() == wrong_email.json()


def test_me_rejects_forged_expired_and_orphan_tokens(client):
    settings = get_settings()
    user_id = signup(client).json()["id"]
    client.cookies.clear()

    forged = jwt.encode({"sub": str(user_id), "exp": datetime.now(UTC) + timedelta(days=1)}, "wrong-secret", "HS256")
    expired = jwt.encode({"sub": str(user_id), "exp": datetime.now(UTC) - timedelta(seconds=1)}, settings.jwt_secret, "HS256")
    no_expiry = jwt.encode({"sub": str(user_id)}, settings.jwt_secret, "HS256")
    unsigned = jwt.encode({"sub": str(user_id), "exp": datetime.now(UTC) + timedelta(days=1)}, None, "none")
    deleted_user = create_token(user_id + 1000)

    for token in (forged, expired, no_expiry, unsigned, deleted_user, "garbage"):
        client.cookies.set(COOKIE_NAME, token)
        assert client.get("/auth/me").status_code == 401, token


def test_health_checks_the_database(client):
    assert client.get("/health").json() == {"status": "ok"}
