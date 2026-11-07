import secrets
import time
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session

from app.core.security import digest
from app.database.session import get_session
from app.persistence.accounts import AccountsRepository
from app.persistence.models import UserModel
from app.presentation.account_schemas import (
    DeleteAccount,
    Login,
    PasswordChange,
    Profile,
    ProfilePatch,
    Register,
    SessionResponse,
)
from app.services.accounts import AccountsService

router = APIRouter(prefix="/api", tags=["accounts"])
Database = Annotated[Session, Depends(get_session)]


def guard(request: Request, db: Session, scope: str, limit: int = 20) -> None:
    if (
        request.method != "GET"
        and request.headers.get("origin") not in request.app.state.settings.allowed_origins
    ):
        raise HTTPException(403, "Origin rejected")
    address = request.client.host if request.client else "unknown"
    if (
        AccountsRepository(db).throttle(digest(scope + ":" + address), int(time.time() // 600))
        > limit
    ):
        raise HTTPException(429, "Too many requests")


def authenticated(
    request: Request, db: Session, mutate: bool = False
) -> tuple[AccountsService, UserModel]:
    service = AccountsService(db)
    token = request.cookies.get("devtreck_session")
    user = service.require(token)
    if mutate:
        expected = digest("csrf:" + str(token))
        supplied = request.headers.get("x-csrf-token", "")
        if not secrets.compare_digest(expected, supplied):
            raise HTTPException(403, "CSRF rejected")
    return service, user


@router.post("/auth/register", response_model=Profile, status_code=201)
def register(payload: Register, request: Request, db: Database) -> Profile:
    guard(request, db, "register", 10)
    user = AccountsService(db).register(payload.name, str(payload.email), payload.password)
    return Profile.model_validate(user)


@router.post("/auth/login", response_model=SessionResponse)
def login(payload: Login, request: Request, response: Response, db: Database) -> SessionResponse:
    guard(request, db, "login")
    if (
        AccountsRepository(db).throttle(
            digest("login-email:" + str(payload.email)), int(time.time() // 600)
        )
        > 10
    ):
        raise HTTPException(429, "Too many requests")
    user, token = AccountsService(db).login(str(payload.email), payload.password)
    response.set_cookie(
        "devtreck_session",
        token,
        max_age=604800,
        httponly=True,
        secure=request.app.state.settings.app_env == "production",
        samesite="strict",
        path="/",
    )
    response.headers["Cache-Control"] = "no-store"
    return SessionResponse(profile=Profile.model_validate(user), csrf_token=digest("csrf:" + token))


@router.get("/auth/csrf")
def csrf(request: Request, response: Response, db: Database) -> dict[str, str]:
    authenticated(request, db)
    response.headers["Cache-Control"] = "no-store"
    return {"csrf_token": digest("csrf:" + request.cookies["devtreck_session"])}


@router.post("/auth/logout", status_code=204)
def logout(request: Request, response: Response, db: Database) -> None:
    guard(request, db, "logout", 60)
    service, _ = authenticated(request, db, True)
    service.logout(request.cookies["devtreck_session"])
    response.delete_cookie("devtreck_session", path="/")


@router.get("/users/me", response_model=Profile)
def me(request: Request, response: Response, db: Database) -> Profile:
    _, user = authenticated(request, db)
    response.headers["Cache-Control"] = "no-store"
    return Profile.model_validate(user)


@router.patch("/users/me", response_model=Profile)
def update(payload: ProfilePatch, request: Request, response: Response, db: Database) -> Profile:
    guard(request, db, "profile", 30)
    service, user = authenticated(request, db, True)
    changes = payload.model_dump(
        exclude_unset=True, exclude={"current_password"}, exclude_none=True
    )
    result = service.update(user, changes, payload.current_password)
    if "email" in changes:
        response.delete_cookie("devtreck_session", path="/")
    return Profile.model_validate(result)


@router.patch("/users/me/password", status_code=204)
def password(payload: PasswordChange, request: Request, response: Response, db: Database) -> None:
    guard(request, db, "password", 10)
    service, user = authenticated(request, db, True)
    service.change_password(user, payload.current_password, payload.new_password)
    response.delete_cookie("devtreck_session", path="/")


@router.delete("/users/me", status_code=204)
def delete(payload: DeleteAccount, request: Request, response: Response, db: Database) -> None:
    guard(request, db, "delete", 10)
    service, user = authenticated(request, db, True)
    service.delete(user, payload.current_password)
    response.delete_cookie("devtreck_session", path="/")
