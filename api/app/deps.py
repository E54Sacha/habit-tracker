"""Shared dependencies for the routes."""

from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .db import get_db
from .models import User
from .security import COOKIE_NAME, read_token

DB = Annotated[Session, Depends(get_db)]


def current_user(db: DB, session: Annotated[str | None, Cookie(alias=COOKIE_NAME)] = None) -> User:
    """The logged-in user, from the session cookie. 401 if missing, invalid, expired or the user was deleted."""
    user_id = read_token(session) if session else None
    user = db.get(User, user_id) if user_id is not None else None
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not logged in")
    return user


CurrentUser = Annotated[User, Depends(current_user)]
