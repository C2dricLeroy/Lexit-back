from datetime import datetime, timedelta

import bcrypt
import jwt
import pytest
from fastapi.exceptions import HTTPException
from sqlalchemy import select
from sqlmodel import Session

from app.config import settings
from app.core.openapi import custom_openapi
from app.core.security.password import (
    check_password,
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
    hash_password,
    invalidate_refresh_token,
    set_refresh_token,
)
from app.main import app
from app.models.userRefreshToken import UserRefreshToken


def test_hash_password():
    """Test hashing a password."""
    password = "test"  # NOSONAR
    hashed_password = hash_password(password)
    assert hashed_password != password
    assert bcrypt.checkpw(
        password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def test_check_password():
    """Test checking if a password matches its hashed version."""
    password = "test"  # NOSONAR
    hashed_password = hash_password(password)
    assert check_password(password, hashed_password)


def test_custom_openapi():
    """Test customizing the OpenAPI schema to include an 'Authorize' security scheme."""
    openapi_schema = custom_openapi(app)
    assert (
        "OAuth2PasswordBearer"
        in openapi_schema["components"]["securitySchemes"]
    )
    assert openapi_schema["security"] == [{"OAuth2PasswordBearer": []}]


def test_create_access_token():
    """Test creating an access token."""
    data = {"sub": "1"}
    token = create_access_token(data)
    payload = decode_access_token(token)
    assert payload["sub"] == data["sub"]


def test_decode_access_token():
    """Test decoding an access token."""
    token = create_access_token({"sub": "1"})
    payload = decode_access_token(token)
    assert payload["sub"] == "1"


def test_decode_refresh_token_invalid_scope():
    """Test decode with invalid scope raises HTTPException."""
    # Token valide + non expiré + mauvaise scope
    data = {"sub": "1", "scope": "access_token"}
    token = create_access_token(data)

    with pytest.raises(HTTPException) as exc_info:
        decode_refresh_token(token)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid token scope"


def test_decode_refresh_token_expired():
    """Test decoding an expired refresh token raises HTTPException."""
    # On force une expiration passée en fixant exp manuellement
    expired_payload = {
        "sub": "1",
        "scope": "refresh_token",
        "exp": 1,  # 1 = 1970-01-01 → toujours expiré
    }

    token = jwt.encode(
        expired_payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    with pytest.raises(HTTPException) as exc_info:
        decode_refresh_token(token)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Refresh token expired"


def test_decode_refresh_token_invalid_signature():
    """Test decoding a refresh token with invalid signature raises HTTPException."""
    token = create_access_token({"sub": "1", "scope": "refresh_token"})

    parts = token.split(".")
    assert len(parts) == 3
    invalid_token = parts[0] + "." + parts[1] + "." + "WRONGSIGNATURE"

    with pytest.raises(HTTPException) as exc_info:
        decode_refresh_token(invalid_token)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid refresh token"


def test_create_refresh_token_successful():
    """Test the successful creation and decoding of a refresh token."""
    user_data = {"sub": "user_123", "role": "admin"}

    token = create_refresh_token(user_data)

    assert isinstance(token, str)
    assert len(token) > 0

    payload = decode_refresh_token(token)

    assert payload["sub"] == user_data["sub"]
    assert payload["role"] == user_data["role"]

    assert payload["scope"] == "refresh_token"
    assert "exp" in payload

    expected_expiry = datetime.now() + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )

    exp_timestamp = payload["exp"]

    time_difference = abs(expected_expiry.timestamp() - exp_timestamp)

    assert time_difference < 5


def test_set_refresh_token(db: Session):
    """Test that set_refresh_token correctly stores a refresh token."""
    user_id = 1
    token = "test_token"
    user_agent = "pytest-agent"

    set_refresh_token(db, user_id=user_id, token=token, user_agent=user_agent)

    statement = select(UserRefreshToken).where(
        UserRefreshToken.refresh_token == token
    )
    stored = db.exec(statement).scalars().first()

    assert stored is not None
    assert stored.user_id == user_id
    assert stored.refresh_token == token
    assert stored.user_agent == user_agent
    assert stored.revoked is False


def test_invalidate_refresh_token_existing(db: Session):
    """Test invalidating an existing refresh token."""
    token = "valid_token"
    refresh = UserRefreshToken(user_id=1, refresh_token=token)
    db.add(refresh)
    db.commit()

    invalidate_refresh_token(db, token)

    statement = select(UserRefreshToken).where(
        UserRefreshToken.refresh_token == token
    )
    stored = db.exec(statement).scalars().first()

    assert stored is not None
    assert stored.revoked is True


def test_invalidate_refresh_token_nonexistent(db: Session):
    """Test invalidating a refresh token that does not exist (should do nothing)."""
    token = "nonexistent_token"

    invalidate_refresh_token(db, token)

    statement = select(UserRefreshToken).where(
        UserRefreshToken.refresh_token == token
    )
    stored = db.exec(statement).scalars().first()

    assert stored is None
