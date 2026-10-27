from app.db.mongo import get_db
from tests.conftest import make_user


def reg(client, **over):
    body = {"name": "Sara Khan", "email": "Sara@Example.com", "password": "Passw0rdOK", "confirm_password": "Passw0rdOK"}
    body.update(over)
    return client.post("/api/auth/register", json=body)


def test_register_success_hides_secrets_and_stores_hash(client):
    r = reg(client)
    assert r.status_code == 201
    data = r.json()
    assert data["email"] == "sara@example.com"  # normalised
    assert "password" not in data and "password_hash" not in data
    stored = get_db().users.find_one({"email": "sara@example.com"})
    assert stored["password_hash"].startswith("$argon2")
    assert "Passw0rdOK" not in str(stored)


def test_duplicate_email_rejected_case_insensitively(client):
    assert reg(client).status_code == 201
    r = reg(client, email="SARA@example.com")
    assert r.status_code == 409 and r.json()["code"] == "email_taken"


def test_registration_validation(client):
    assert reg(client, confirm_password="different1").status_code == 422
    assert reg(client, password="short1", confirm_password="short1").status_code == 422
    assert reg(client, password="onlyletters", confirm_password="onlyletters").status_code == 422
    assert reg(client, email="not-an-email").status_code == 422
    r = reg(client, name="   ")
    assert r.status_code == 422 and r.json()["code"] == "validation_error"


def test_login_and_me(client):
    reg(client)
    r = client.post("/api/auth/login", json={"email": "sara@example.com", "password": "Passw0rdOK"})
    assert r.status_code == 200 and r.json()["token_type"] == "bearer"
    token = r.json()["access_token"]
    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200 and me.json()["name"] == "Sara Khan"


def test_wrong_password_and_unknown_email_look_identical(client):
    reg(client)
    bad_pw = client.post("/api/auth/login", json={"email": "sara@example.com", "password": "wrongpass1"})
    unknown = client.post("/api/auth/login", json={"email": "nobody@example.com", "password": "wrongpass1"})
    assert bad_pw.status_code == unknown.status_code == 401
    assert bad_pw.json()["detail"] == unknown.json()["detail"]


def test_protected_endpoints_reject_anonymous_and_bad_tokens(client):
    for method, url in [
        ("get", "/api/auth/me"), ("post", "/api/auth/logout"), ("get", "/api/conversations"),
        ("post", "/api/conversations"), ("get", "/api/conversations/abc"),
        ("patch", "/api/conversations/abc"), ("delete", "/api/conversations/abc"),
        ("post", "/api/conversations/abc/messages"),
    ]:
        assert getattr(client, method)(url).status_code == 401, (method, url)
    assert client.get("/api/auth/me", headers={"Authorization": "Bearer garbage"}).status_code == 401


def test_logout_invalidates_token(client):
    headers = make_user(client)
    assert client.get("/api/auth/me", headers=headers).status_code == 200
    assert client.post("/api/auth/logout", headers=headers).status_code == 204
    assert client.get("/api/auth/me", headers=headers).status_code == 401


def test_expired_token_rejected(client, monkeypatch):
    import jwt
    from datetime import datetime, timedelta, timezone
    from app.core.config import get_settings

    headers = make_user(client)
    uid = client.get("/api/auth/me", headers=headers).json()["id"]
    s = get_settings()
    old = jwt.encode({"sub": uid, "jti": "x1", "exp": datetime.now(timezone.utc) - timedelta(minutes=1)},
                     s.jwt_secret_key, algorithm=s.jwt_algorithm)
    assert client.get("/api/auth/me", headers={"Authorization": f"Bearer {old}"}).status_code == 401
