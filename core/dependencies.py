from collections.abc import Callable

from fastapi import HTTPException, Request, status

from repositories.university_repository import get_user_by_id


def get_current_user(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    user = get_user_by_id(user_id)
    if user is None or not user["is_active"]:
        request.session.clear()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    return user


def require_roles(*roles: str) -> Callable:
    def dependency(request: Request):
        user = get_current_user(request)
        if user["role"] not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
        return user

    return dependency
