from fastapi import HTTPException

from app.security.permissions import require_role


def test_allows_required_role():
    dep = require_role("admin")
    assert dep({"id": "u1", "role": "admin"})["id"] == "u1"


def test_rejects_insufficient_role():
    dep = require_role("admin")
    try:
        dep({"id": "u1", "role": "user"})
    except HTTPException as exc:
        assert exc.status_code == 403
    else:
        raise AssertionError("expected HTTPException")
