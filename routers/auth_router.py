from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import RedirectResponse

from schemas.auth_schema import LoginRequest
from services.auth_service import authenticate, register_student


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login")
def api_login(data: LoginRequest):
    user = authenticate(data.username, data.password)
    if user is None:
        raise HTTPException(status_code=401, detail="Username or password is incorrect")
    return {"id": user["id"], "username": user["username"], "role": user["role"]}


@router.post("/web-login", include_in_schema=False)
def web_login(request: Request, username: str = Form(...), password: str = Form(...)):
    user = authenticate(username, password)
    if user is None:
        return RedirectResponse(url="/?error=1", status_code=303)
    request.session["user_id"] = user["id"]
    return RedirectResponse(url="/dashboard", status_code=303)


@router.post("/register", include_in_schema=False)
def register(fullname: str = Form(...), username: str = Form(...), password: str = Form(...)):
    try:
        register_student(fullname, username, password)
    except ValueError:
        return RedirectResponse(url="/register?error=1", status_code=303)
    return RedirectResponse(url="/?registered=1", status_code=303)


@router.post("/logout", include_in_schema=False)
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)
