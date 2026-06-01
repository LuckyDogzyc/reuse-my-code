from __future__ import annotations

from collections.abc import Callable

from fastapi import HTTPException, status


def require_role(required_role: str) -> Callable[[dict], dict]:
    def dependency(current_user: dict) -> dict:
        if current_user.get("role") != required_role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="insufficient role")
        return current_user

    return dependency
