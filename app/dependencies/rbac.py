from __future__ import annotations

from typing import Callable, Iterable

from fastapi import Depends, HTTPException, status

from app.dependencies.auth import get_current_user
from app.models.user import User


def require_roles(*allowed: str) -> Callable:
    """
    Dependency: requires that current_user has at least one of allowed roles by code.
    Example:
        @router.post(..., dependencies=[Depends(require_roles("staff","admin"))])
    """

    allowed_set = set(allowed)

    def _dep(current_user: User = Depends(get_current_user)) -> User:
        user_role_codes = {r.code for r in (current_user.roles or [])}
        if not (user_role_codes & allowed_set):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return _dep
