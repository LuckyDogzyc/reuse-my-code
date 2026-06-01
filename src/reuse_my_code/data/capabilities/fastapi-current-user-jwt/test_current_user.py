from fastapi import HTTPException
from jose import jwt

from app.security import current_user


def test_missing_bearer_token_is_rejected():
    try:
        current_user.get_current_user(None)
    except HTTPException as exc:
        assert exc.status_code == 401
    else:
        raise AssertionError("expected HTTPException")


def test_decodes_subject_claim(monkeypatch):
    monkeypatch.setattr(current_user, "get_jwt_secret", lambda: "secret")
    token = jwt.encode({"sub": "u1", "role": "admin"}, "secret", algorithm="HS256")
    credentials = type("Cred", (), {"scheme": "Bearer", "credentials": token})()
    assert current_user.get_current_user(credentials) == {"id": "u1", "role": "admin"}
