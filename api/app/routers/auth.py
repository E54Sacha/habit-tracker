"""Sign up, log in, log out, and "who am I"."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Response, status
from pydantic import BaseModel, EmailStr, Field, StringConstraints
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from ..config import get_settings
from ..deps import DB, CurrentUser
from ..models import User
from ..security import COOKIE_NAME, create_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])

Email = Annotated[EmailStr, StringConstraints(max_length=254)]


class SignUp(BaseModel):
    email: Email
    # 8 minimum (NIST guidance); 128 maximum so nobody makes the server hash a megabyte.
    password: str = Field(min_length=8, max_length=128)


class LogIn(BaseModel):
    email: Email
    password: str = Field(min_length=1, max_length=128)


class UserOut(BaseModel):
    id: int
    email: str


def _set_session(response: Response, user_id: int) -> None:
    settings = get_settings()
    response.set_cookie(
        COOKIE_NAME,
        create_token(user_id),
        max_age=settings.token_days * 24 * 3600,
        httponly=True,  # JavaScript can't read it, so an XSS bug can't steal it
        secure=settings.cookie_secure,  # HTTPS only in production
        samesite="lax",  # not sent on POSTs from other sites (CSRF protection)
        path="/",
    )


@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(body: SignUp, db: DB, response: Response) -> UserOut:
    user = User(email=body.email.lower(), password_hash=hash_password(body.password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError:  # the unique email constraint: also safe when two sign-ups race
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "An account with this email already exists") from None
    _set_session(response, user.id)
    return UserOut(id=user.id, email=user.email)


@router.post("/login")
def login(body: LogIn, db: DB, response: Response) -> UserOut:
    user = db.scalar(select(User).where(User.email == body.email.lower()))
    # Same message for a wrong email and a wrong password: don't reveal which accounts exist.
    if not verify_password(body.password, user.password_hash if user else None):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Wrong email or password")
    _set_session(response, user.id)
    return UserOut(id=user.id, email=user.email)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response) -> None:
    settings = get_settings()
    response.delete_cookie(COOKIE_NAME, path="/", httponly=True, secure=settings.cookie_secure, samesite="lax")


@router.get("/me")
def me(user: CurrentUser) -> UserOut:
    return UserOut(id=user.id, email=user.email)
