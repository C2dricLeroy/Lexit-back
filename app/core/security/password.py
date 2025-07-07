from datetime import datetime, timedelta
from typing import Optional

import bcrypt
import jwt
from fastapi import HTTPException
from sqlalchemy import desc
from sqlmodel import Session, select

from app.config import settings
from app.models import UserRefreshToken


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def check_password(password: str, hashed_password: str) -> bool:
    """Check if a password matches its hashed version."""
    return bcrypt.checkpw(
        password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def create_access_token(
    data: dict, expires_delta: Optional[timedelta] = None
) -> str:
    """Create an access token using the provided data."""
    to_encode = data.copy()
    expire = datetime.now() + (
        expires_delta
        or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        payload=to_encode,
        key=settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """Decode an access token."""
    try:
        payload = jwt.decode(
            token,
            key=settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=401, detail="Token has expired"
        ) from exc
    except jwt.InvalidTokenError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc


def create_refresh_token(data: dict) -> str:
    """Create a refresh token with a longer expiration and 'refresh_token' scope."""
    to_encode = data.copy()
    expire = datetime.now() + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    to_encode.update(
        {
            "exp": expire,
            "scope": "refresh_token",
        }
    )
    encoded_jwt = jwt.encode(
        payload=to_encode,
        key=settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt


def decode_refresh_token(token: str) -> dict:
    """Decode a refresh token and verify its scope."""
    try:
        payload = jwt.decode(
            token,
            key=settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        if payload.get("scope") != "refresh_token":
            raise HTTPException(status_code=401, detail="Invalid token scope")
        return payload
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=401, detail="Refresh token expired"
        ) from exc
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=401, detail="Invalid refresh token"
        ) from exc


def set_refresh_token(
    db: Session, user_id: int, token: str, user_agent: str = None
):
    """Set the new refresh_token on provided User."""
    db_token = UserRefreshToken(
        user_id=user_id, refresh_token=token, user_agent=user_agent
    )
    db.add(db_token)
    db.commit()


def invalidate_refresh_token(db: Session, token: str):
    """Invalidate last refresh token of the User."""
    statement = (
        select(UserRefreshToken)
        .where(UserRefreshToken.refresh_token == token)
        .order_by(desc(UserRefreshToken.created_at))
    )
    db_token = db.exec(statement).first()
    if db_token:
        db_token.revoked = True
        db.add(db_token)
        db.commit()
