from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from app.dto.socialLogin import SocialLoginRequest
from app.models.user import User
from app.models.userProvider import UserProvider
from app.routes.social import social_login


@pytest.mark.asyncio
async def test_social_login_unsupported_provider():
    """Test that social login returns an error when an unsupported provider is used."""
    payload = SocialLoginRequest(provider="facebook", access_token="token")
    with pytest.raises(HTTPException) as exc:
        await social_login(payload, MagicMock())
    assert exc.value.status_code == 400
    assert exc.value.detail == "Unsupported provider"


@pytest.mark.asyncio
async def test_social_login_invalid_token():
    """Test that social login returns an error when an invalid token is used."""
    payload = SocialLoginRequest(provider="google", access_token="bad-token")
    mock_session = MagicMock()

    fake_response = MagicMock(status_code=401)
    fake_response.json.return_value = {}

    client_mock = AsyncMock()
    client_mock.__aenter__.return_value = client_mock
    client_mock.get = AsyncMock(return_value=fake_response)

    with patch(
        "app.routes.social.httpx.AsyncClient", return_value=client_mock
    ):
        with pytest.raises(HTTPException) as exc:
            await social_login(payload, mock_session)

    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid token"


@pytest.mark.asyncio
async def test_social_login_existing_user():
    """Test that social login returns an existing user."""
    payload = SocialLoginRequest(provider="google", access_token="good-token")
    mock_session = MagicMock()

    existing_user = User(id=1, email="user@example.com", username="Existing")
    user_provider = UserProvider(
        provider="google", provider_user_id="google-123", user_id=1
    )
    user_provider.user = existing_user

    mock_result = MagicMock()
    mock_result.first.return_value = user_provider
    mock_session.exec.return_value = mock_result

    fake_response = MagicMock(status_code=200)
    fake_response.json.return_value = {
        "sub": "google-123",
        "email": existing_user.email,
        "name": existing_user.username,
    }

    client_mock = AsyncMock()
    client_mock.__aenter__.return_value = client_mock
    client_mock.get = AsyncMock(return_value=fake_response)

    with patch(
        "app.routes.social.httpx.AsyncClient", return_value=client_mock
    ):
        with patch(
            "app.routes.social.create_access_token",
            return_value="access-token",
        ):
            with patch(
                "app.routes.social.create_refresh_token",
                return_value="refresh-token",
            ):
                with patch(
                    "app.routes.social.email_queue.enqueue"
                ) as mock_enqueue:
                    result = await social_login(payload, mock_session)

    assert result == {
        "access_token": "access-token",
        "refresh_token": "refresh-token",
    }
    mock_session.exec.assert_called_once()
    mock_session.add.assert_not_called()
    mock_session.commit.assert_called_once()
    mock_enqueue.assert_not_called()


@pytest.mark.asyncio
async def test_social_login_new_user():
    """Test that social login returns a new user."""
    payload = SocialLoginRequest(provider="google", access_token="good-token")
    mock_session = MagicMock()

    mock_result = MagicMock()
    mock_result.first.return_value = None
    mock_session.exec.return_value = mock_result

    fake_response = MagicMock(status_code=200)
    fake_response.json.return_value = {
        "sub": "google-789",
        "email": "new@example.com",
        "name": "New User",
    }

    client_mock = AsyncMock()
    client_mock.__aenter__.return_value = client_mock
    client_mock.get = AsyncMock(return_value=fake_response)

    with patch(
        "app.routes.social.httpx.AsyncClient", return_value=client_mock
    ):
        with patch(
            "app.routes.social.create_access_token",
            return_value="access-token",
        ):
            with patch(
                "app.routes.social.create_refresh_token",
                return_value="refresh-token",
            ):
                with patch(
                    "app.routes.social.email_queue.enqueue"
                ) as mock_enqueue:
                    result = await social_login(payload, mock_session)

    assert result == {
        "access_token": "access-token",
        "refresh_token": "refresh-token",
    }
    mock_session.add.assert_any_call(
        pytest.helpers.any_instance_of(User)
        if hasattr(pytest, "helpers")
        else mock_session.add.call_args_list[0][0][0]  # type: ignore
    )
    mock_session.flush.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_enqueue.assert_called_once()
