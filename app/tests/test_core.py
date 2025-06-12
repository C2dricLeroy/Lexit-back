import bcrypt

from app.core.openapi import custom_openapi
from app.core.security.password import (
    check_password,
    create_access_token,
    decode_access_token,
    hash_password,
)
from app.main import app


def test_hash_password():
    """Test hashing a password."""
    password = "test"
    hashed_password = hash_password(password)
    assert hashed_password != password
    assert bcrypt.checkpw(
        password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def test_check_password():
    """Test checking if a password matches its hashed version."""
    password = "test"
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
