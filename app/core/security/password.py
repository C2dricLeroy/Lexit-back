from datetime import datetime, timedelta
from typing import Optional

import bcrypt
import jwt
from fastapi import HTTPException

from app.config import settings


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
