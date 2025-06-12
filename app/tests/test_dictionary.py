from unittest.mock import MagicMock, patch

import pytest
from fastapi.exceptions import HTTPException
from sqlalchemy.exc import IntegrityError
from starlette.requests import Request

from app.dto.dictionary import DictionaryCreate, DictionaryUpdate
from app.models.dictionary import Dictionary
from app.models.language import Language
from app.models.user import User
from app.routes.dictionary import (
    create_dictionary,
    delete_dictionary,
    get_dictionaries,
    get_dictionary_by_id,
    update_dictionary,
)
from app.services.dictionary import compute_display_name

fake_scope = {
    "type": "http",
    "path": "/",
    "headers": [],
    "client": ("127.0.0.1", 12345),
    "method": "GET",
}

request = Request(scope=fake_scope)


def test_create_dictionary_success():
    """Test creating a dictionary with success."""
    mock_session = MagicMock()

    mock_user = MagicMock(spec=User)
    mock_user.id = 1
    mock_user.dictionaries = []

    mock_user_from_db = User(id=1, email="test@example.com")
    mock_user_from_db.dictionaries = []
    mock_session.get.return_value = mock_user_from_db

    dictionary_data = DictionaryCreate(
        name="Test Dictionary",
        source_language_id=1,
        target_language_id=1,
    )

    mock_source_language = MagicMock(id=1)
    mock_target_language = MagicMock(id=1)

    with patch(
        "app.routes.dictionary.compute_display_name",
        return_value=Dictionary(
            name="Test Dictionary",
            source_language=mock_source_language,
            target_language=mock_target_language,
            display_name="Test Dictionary (en → fr)",
            user_id=1,
        ),
    ):
        result = create_dictionary(
            request, dictionary_data, mock_user, mock_session
        )

        assert result.name == "Test Dictionary"
        assert result.source_language == mock_source_language
        assert result.target_language == mock_target_language
        assert result.user_id == 1
        assert mock_session.commit.called
        assert mock_session.refresh.called
        assert len(mock_user_from_db.dictionaries) == 1


def test_create_dictionary_user_not_found():
    """Test creating a dictionary with a non-existent user."""
    mock_user = MagicMock(spec=User)
    mock_user.id = 1
    mock_user.dictionaries = []

    mock_session = MagicMock()
    mock_session.get.return_value = None

    dictionary_data = DictionaryCreate(
        name="Test Dictionary",
        source_language_id=1,
        target_language_id=1,
    )

    with pytest.raises(HTTPException) as exc_info:
        create_dictionary(request, dictionary_data, mock_user, mock_session)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User not found"
    mock_session.commit.assert_not_called()


def test_create_dictionary_integrity_error():
    """Test creating a dictionary with a duplicate language combination."""
    mock_session = MagicMock()
    mock_user = User(id=1, email="test@example.com")
    mock_user.dictionaries = []
    mock_session.get.return_value = mock_user

    dictionary_data = DictionaryCreate(
        name="Test Dictionary",
        source_language_id=1,
        target_language_id=1,
        user_id=1,
    )

    mock_session.commit.side_effect = IntegrityError(
        "statement", "params", "orig"
    )

    mock_source_language = MagicMock(id=1)
    mock_target_language = MagicMock(id=1)

    with patch(
        "app.routes.dictionary.compute_display_name",
        return_value=Dictionary(
            name="Test Dictionary",
            source_language=mock_source_language,
            target_language=mock_target_language,
            user_id=1,
            display_name="Test Dictionary (en → fr)",
        ),
    ):
        with pytest.raises(HTTPException) as exc_info:
            create_dictionary(
                request, dictionary_data, mock_user, mock_session
            )

        assert exc_info.value.status_code == 409
        assert (
            exc_info.value.detail
            == "A dictionary with these languages already exists."
        )
        mock_session.rollback.assert_called_once()


def test_get_dictionaries():
    """Test retrieving all dictionaries successfully."""
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

    mock_query_result = MagicMock()
    mock_query_result.all.return_value = mock_dictionaries
    mock_session.exec.return_value = mock_query_result

    result = get_dictionaries(request, mock_session)

    assert result == mock_dictionaries
    assert len(result) == 2
    assert result[0].name == "English to French"
    assert result[1].name == "English to Spanish"
    mock_session.exec.assert_called_once()
    mock_query_result.all.assert_called_once()


def test_get_dictionaries_empty():
    """Test retrieving dictionaries when none exist."""
    mock_session = MagicMock()

    mock_query_result = MagicMock()
    mock_query_result.all.return_value = []
    mock_session.exec.return_value = mock_query_result

    result = get_dictionaries(request, mock_session)

    assert result == []
    assert len(result) == 0
    mock_session.exec.assert_called_once()
    mock_query_result.all.assert_called_once()


def test_get_dictionary_by_id_success():
    """Test retrieving a dictionary by ID successfully."""
    mock_session = MagicMock()

    mock_dictionary = Dictionary(
        id=1,
        name="English to French",
        display_name="English to French (en → fr)",
        source_language_id=1,
        target_language_id=2,
        user_id=1,
    )

    mock_query_result = MagicMock()
    mock_query_result.first.return_value = mock_dictionary
    mock_session.exec.return_value = mock_query_result

    result = get_dictionary_by_id(request, 1, mock_session)

    assert result == mock_dictionary
    assert result.id == 1
    assert result.name == "English to French"
    assert result.display_name == "English to French (en → fr)"
    mock_session.exec.assert_called_once()
    mock_query_result.first.assert_called_once()


def test_update_dictionary_success():
    """Test updating a dictionary with success."""
    mock_session = MagicMock()
    mock_user = User(id=1, email="test@example.com")

    mock_dictionary = Dictionary(
        id=1,
        name="English to French",
        display_name="English to French (en → fr)",
        source_language_id=1,
        target_language_id=2,
        user_id=1,
    )

    mock_session.get.return_value = mock_dictionary

    dictionary_update = DictionaryUpdate(name="Updated Dictionary Name")

    result = update_dictionary(
        request, 1, dictionary_update, mock_user, mock_session
    )

    assert result.id == 1
    assert result.name == "Updated Dictionary Name"
    assert result.display_name == "English to French (en → fr)"
    assert result.source_language_id == 1
    assert result.target_language_id == 2

    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(mock_dictionary)


def test_delete_dictionary_success():
    """Test deleting a dictionary that exists returns 204 status code."""
    mock_session = MagicMock()
    mock_user = User(id=1, email="test@example.com")

    mock_dictionary = Dictionary(
        id=1,
        name="English to French",
        display_name="English to French (en → fr)",
        source_language_id=1,
        target_language_id=2,
        user_id=1,
    )

    mock_session.get.return_value = mock_dictionary

    result = delete_dictionary(
        request, dictionary_id=1, current_user=mock_user, session=mock_session
    )

    assert result == {"message": "Dictionary %s deleted successfully!", 1: 1}
    mock_session.delete.assert_called_once_with(mock_dictionary)
    mock_session.commit.assert_called_once()


def test_delete_dictionary_not_found():
    """Test that deleting a non-existent dictionary raises a 404 error."""
    mock_session = MagicMock()
    mock_user = User(id=1, email="test@example.com")
    mock_session.get.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        delete_dictionary(request, 999, mock_user, mock_session)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Dictionary not found"
    mock_session.delete.assert_not_called()
    mock_session.commit.assert_not_called()


def test_compute_display_name():
    """Test computing the display name for a dictionary."""
    mock_dictionary = Dictionary(
        source_language=Language(id=1, name="English"),
        target_language=Language(id=2, name="French"),
    )
    result = compute_display_name(
        mock_dictionary,
    )

    assert result.display_name == "English : French"
