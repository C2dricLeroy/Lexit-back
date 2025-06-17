from unittest.mock import MagicMock, patch

import pytest
from fastapi.exceptions import HTTPException
from starlette.requests import Request

from app.dto.user import UserCreate
from app.models.dictionary import Dictionary
from app.models.user import User
from app.routes.user import (
    admin_delete_user,
    create_user,
    get_user_by_id,
    get_user_dictionaries,
    get_users,
)
from app.services.user import get_current_user

fake_scope = {
    "type": "http",
    "path": "/",
    "headers": [],
    "client": ("127.0.0.1", 12345),
    "method": "GET",
}

request = Request(scope=fake_scope)


def test_get_users():
    """Test that get_users returns all users when multiple users exist."""
    mock_session = MagicMock()

    mock_users = [
        User(
            id=1,
            username="user1",
            email="user1@example.com",
            hashed_password="hashed1",  # NOSONAR
        ),
        User(
            id=2,
            username="user2",
            email="user2@example.com",
            hashed_password="hashed2",  # NOSONAR
        ),
    ]

    mock_query_result = MagicMock()
    mock_query_result.all.return_value = mock_users
    mock_session.exec.return_value = mock_query_result

    result = get_users(request, mock_session)

    assert result == mock_users
    assert len(result) == 2
    assert result[0].username == "user1"
    assert result[1].username == "user2"
    mock_session.exec.assert_called_once()
    mock_query_result.all.assert_called_once()


def test_get_user_by_id():
    """Test that get_user_by_id returns the correct user when a valid ID is provided."""
    mock_session = MagicMock()

    mock_user = User(
        id=1,
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password",  # NOSONAR
    )

    mock_query_result = MagicMock()
    mock_query_result.first.return_value = mock_user
    mock_session.exec.return_value = mock_query_result

    result = get_user_by_id(request, user_id=1, session=mock_session)

    assert result == mock_user
    assert result.id == 1
    assert result.username == "testuser"
    assert result.email == "test@example.com"
    mock_session.exec.assert_called_once()
    mock_query_result.first.assert_called_once()


def test_get_user_dictionaries_empty():
    """Test that get_user_dictionaries returns an empty list when the user has no dictionaries."""
    mock_session = MagicMock()

    mock_user = MagicMock(spec=User)
    mock_user.id = 1
    mock_user.dictionaries = []

    mock_session.get.return_value = mock_user

    mock_current_user = MagicMock()
    mock_current_user.id = 1

    result = get_user_dictionaries(
        request=MagicMock(spec=Request),
        current_user=mock_current_user,
        session=mock_session,
    )

    assert result == []
    assert len(result) == 0


def test_get_user_dictionaries_multiple():
    """Test that get_user_dictionaries returns multiple dictionaries when the user has created several."""
    mock_session = MagicMock()

    mock_dictionaries = [
        Dictionary(
            id=1,
            name="English to French",
            display_name="English to French (en → fr)",
            source_language_id=1,
            target_language_id=2,
            user_id=1,
        ),
        Dictionary(
            id=2,
            name="English to Spanish",
            display_name="English to Spanish (en → es)",
            source_language_id=1,
            target_language_id=3,
            user_id=1,
        ),
    ]

    mock_user = MagicMock(spec=User)
    mock_user.id = 1
    mock_user.dictionaries = mock_dictionaries

    mock_session.get.return_value = mock_user

    mock_current_user = MagicMock()
    mock_current_user.id = 1

    result = get_user_dictionaries(
        request=MagicMock(spec=Request),
        current_user=mock_current_user,
        session=mock_session,
    )

    assert result == mock_dictionaries
    assert len(result) == 2
    assert result[0].name == "English to French"
    assert result[1].name == "English to Spanish"
    assert result[0].user_id == 1
    assert result[1].user_id == 1


def test_create_user_success():
    """Test creating a user with all required fields successfully."""
    mock_session = MagicMock()

    user_data = UserCreate(
        username="newuser",
        email="newuser@example.com",
        password="password123",
        is_active=True,
        is_superuser=False,
    )

    with patch(
        "app.routes.user.hash_password",
        return_value="hashed_password123",  # NOSONAR
    ):
        result = create_user(request, user_data, mock_session)

        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()

        assert result.username == "newuser"
        assert result.email == "newuser@example.com"
        assert result.hashed_password == "hashed_password123"  # NOSONAR
        assert result.is_active is True
        assert result.is_superuser is False


def test_get_current_user():
    """Test that get_current_user returns the correct user when a valid JWT token is provided."""
    mock_session = MagicMock()
    mock_user = User(
        id=1,
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password",
    )

    mock_query_result = MagicMock()
    mock_query_result.first.return_value = mock_user
    mock_session.exec.return_value = mock_query_result

    token = "fake.jwt.token"  # NOSONAR

    with patch("app.services.user.decode_access_token") as mock_decode:
        mock_decode.return_value = {"sub": "1"}

        result = get_current_user(token=token, session=mock_session)

        assert result == mock_user
        assert result.id == 1
        assert result.username == "testuser"
        assert result.email == "test@example.com"
        mock_session.exec.assert_called_once()


def test_admin_delete_user_success():
    """Test that admin_delete_user deletes the user successfully."""
    mock_session = MagicMock()
    mock_admin_user = User(
        id=1,
        username="adminuser",
        email="admin@example.com",
        hashed_password="hashed_password",
        is_active=True,
        is_superuser=True,
    )

    mock_user = User(
        id=3,
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password",
    )

    mock_session.get.return_value = mock_user

    result = admin_delete_user(request, 3, mock_admin_user, mock_session)

    assert result == {"message": "User deleted successfully"}
    mock_session.delete.assert_called_once()
    mock_session.commit.assert_called_once()


def test_admin_delete_himself():
    """Test that admin_delete_user raises an error when trying to delete themselves."""
    mock_session = MagicMock()
    mock_admin_user = User(
        id=1,
        username="adminuser",
        email="admin@example.com",
        hashed_password="hashed_password",
        is_active=True,
        is_superuser=True,
    )

    mock_session.get.return_value = mock_admin_user

    with pytest.raises(HTTPException) as http_exeception:
        admin_delete_user(request, 1, mock_admin_user, mock_session)

    assert http_exeception.value.detail == "Cannot delete yourself"
    assert http_exeception.value.status_code == 403


def test_admin_delete_not_found():
    """Test that deleting a non-existent dictionary as an admin raises a 404 error."""
    mock_session = MagicMock()
    mock_admin_user = User(
        id=1,
        email="admin@example.com",
        is_superuser=True,
    )

    mock_session.get.return_value = None

    with pytest.raises(HTTPException) as http_exeception:
        admin_delete_user(request, 999, mock_admin_user, mock_session)

    assert http_exeception.value.detail == "User not found"
    assert http_exeception.value.status_code == 404


def test_admin_delete_user_not_superuser():
    """Test that deleting a user as a regular user raises a 403 error."""
    mock_session = MagicMock()
    mock_regular_user = User(
        id=2,
        email="regular@example.com",
        is_superuser=False,
    )

    mock_deleted_user = User(
        id=3,
        email="regular@example.com",
        is_superuser=False,
    )

    mock_session.get.return_value = mock_deleted_user

    with pytest.raises(HTTPException) as http_exeception:
        admin_delete_user(request, 3, mock_regular_user, mock_session)

    assert (
        http_exeception.value.detail
        == "You are not authorized to delete this user."
    )
    assert http_exeception.value.status_code == 403
