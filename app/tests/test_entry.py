from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from fastapi.exceptions import HTTPException
from sqlalchemy.exc import IntegrityError
from starlette.requests import Request

from app.dto.entry import EntryCreate, EntryUpdate
from app.models.dictionary import Dictionary
from app.models.entry import Entry
from app.routes.entry import (
    create_entry,
    delete_entry,
    get_entries,
    get_entries_by_dictionary_id,
    get_entry_by_id,
    update_entry,
)
from app.services.entry import compute_display_name

fake_scope = {
    "type": "http",
    "path": "/",
    "headers": [],
    "client": ("127.0.0.1", 12345),
    "method": "GET",
}

request = Request(scope=fake_scope)


def test_get_entries():
    """Test that get_entries returns all entries."""
    mock_session = MagicMock()

    mock_entries = [
        Entry(
            original_name="Entry 1", translation="entrée 1", dictionary_id=1
        ),
        Entry(
            original_name="Entry 2", translation="entrée 2", dictionary_id=1
        ),
    ]

    mock_query_result = MagicMock()
    mock_query_result.all.return_value = mock_entries
    mock_session.exec.return_value = mock_query_result

    response = get_entries(request, mock_session)

    assert response == mock_entries
    assert len(response) == 2
    assert response[0].original_name == "Entry 1"
    assert response[1].original_name == "Entry 2"
    mock_session.exec.assert_called_once()
    mock_query_result.all.assert_called_once()


def test_get_entry_by_id():
    """Test that get_entry_by_id returns the correct entry when a valid ID is provided."""
    mock_session = MagicMock()

    mock_entry = Entry(
        id=1,
        original_name="Test Entry",
        translation="Entrée de test",
        dictionary_id=1,
    )

    mock_query_result = MagicMock()
    mock_query_result.first.return_value = mock_entry
    mock_session.exec.return_value = mock_query_result

    response = get_entry_by_id(request, entry_id=1, session=mock_session)

    assert response == mock_entry
    assert response.id == 1
    assert response.original_name == "Test Entry"
    mock_session.exec.assert_called_once()
    mock_query_result.first.assert_called_once()


def test_get_entries_by_dictionary_id():
    """Test that get_entries_by_dictionary_id returns all entries for a valid dictionary ID."""
    mock_session = MagicMock()

    mock_entries = [
        Entry(
            original_name="Dictionary Entry 1",
            translation="entrée dictionnaire 1",
            dictionary_id=1,
        ),
        Entry(
            original_name="Dictionary Entry 2",
            translation="entrée dictionnaire 2",
            dictionary_id=1,
        ),
    ]

    mock_query_result = MagicMock()
    mock_query_result.all.return_value = mock_entries
    mock_session.exec.return_value = mock_query_result

    response = get_entries_by_dictionary_id(
        request, dictionary_id=1, session=mock_session
    )

    assert response == mock_entries
    assert len(response) == 2
    assert response[0].original_name == "Dictionary Entry 1"
    assert response[1].original_name == "Dictionary Entry 2"
    assert response[0].dictionary_id == 1
    assert response[1].dictionary_id == 1
    mock_session.exec.assert_called_once()
    mock_query_result.all.assert_called_once()


def test_create_entry():
    """Test that create_entry properly creates and returns a new entry."""
    mock_session = MagicMock()

    mock_dictionary = Dictionary(
        id=1,
        username="testuser",
        email="test@example.com",
        hashed_password="hashed",  # NOSONAR
    )
    mock_dictionary.entries = []
    mock_session.get.return_value = mock_dictionary

    entry_data = EntryCreate(
        id=1,
        original_name="New Entry",
        translation="Nouvelle entrée",
        dictionary_id=1,
    )

    with patch(
        "app.services.entry.compute_display_name",
        return_value=Entry(
            id=1,
            original_name="New Entry",
            translation="Nouvelle entrée",
            dictionary_id=1,
            display_name="Test entries (en → fr)",
        ),
    ):
        response = create_entry(request, entry_data, mock_session)

        assert response.original_name == "New Entry"
        assert response.translation == "Nouvelle entrée"
        assert response.dictionary_id == 1
        mock_session.commit.assert_called_once()
        assert len(mock_dictionary.entries) == 1


def test_create_entry_dictionary_not_found():
    """Test that create_entry raises HTTPException when the dictionary is not found."""
    mock_session = MagicMock()
    mock_session.get.return_value = None

    entry_data = EntryCreate(
        id=1,
        original_name="New Entry",
        translation="Nouvelle entrée",
        dictionary_id=999,
    )

    with pytest.raises(HTTPException) as excinfo:
        create_entry(request, entry_data, mock_session)

    assert excinfo.value.status_code == 404
    assert excinfo.value.detail == "Dictionary not found"
    mock_session.get.assert_called_once()

    mock_session.add.assert_not_called()
    mock_session.commit.assert_not_called()
    mock_session.refresh.assert_not_called()


def test_create_entry_integrity_error():
    """Test creating an entry that violates the unique constraint."""
    mock_session = MagicMock()

    entry_data = EntryCreate(
        original_name="Bonjour", translation="Hello", dictionary_id=1
    )

    mock_session.commit.side_effect = IntegrityError(
        "statement", "params", "orig"
    )

    with patch(
        "app.routes.entry.compute_display_name",
        return_value=Entry(
            original_name="Bonjour",
            translation="Hello",
            dictionary_id=1,
            display_name="Bonjour (→ Hello)",
        ),
    ):
        with pytest.raises(HTTPException) as exc_info:
            create_entry(request, entry_data, mock_session)

        assert exc_info.value.status_code == 409
        assert (
            exc_info.value.detail
            == "An entry with this name already exists in the dictionary."
        )
        mock_session.rollback.assert_called_once()


def test_delete_entry_success():
    """Test that delete_entry returns a success message when successfully deleting an entry."""
    mock_session = MagicMock()

    entry_id = 1
    mock_entry = Entry(
        id=entry_id,
        original_name="Test Entry",
        translation="Entrée de test",
        dictionary_id=1,
    )

    mock_session.get.return_value = mock_entry

    response = delete_entry(request, entry_id=entry_id, session=mock_session)

    assert response == {
        "message": "Entry %s deleted successfully!",
        entry_id: entry_id,
    }
    mock_session.get.assert_called_once_with(Entry, entry_id)
    mock_session.delete.assert_called_once_with(mock_entry)
    mock_session.commit.assert_called_once()
    mock_session.rollback.assert_not_called()


def test_delete_entry_not_found():
    """Test that delete_entry raises a 404 HTTPException when the entry is not found."""
    mock_session = MagicMock()

    entry_id = 999
    mock_session.get.return_value = None

    with pytest.raises(HTTPException) as excinfo:
        delete_entry(request, entry_id=entry_id, session=mock_session)

    assert excinfo.value.status_code == 404
    assert excinfo.value.detail == "Entry not found"
    mock_session.get.assert_called_once_with(Entry, entry_id)
    mock_session.delete.assert_not_called()
    mock_session.commit.assert_not_called()
    mock_session.rollback.assert_not_called()


def test_update_entry_success():
    """Test that update_entry successfully updates an entry with valid input."""
    mock_session = MagicMock()

    entry_id = 1
    mock_entry = Entry(
        id=entry_id,
        original_name="Original Entry",
        translation="Translation originale",
        dictionary_id=1,
    )

    mock_session.get.return_value = mock_entry

    entry_update = EntryUpdate(original_name="Updated Entry")

    with patch(
        "app.routes.entry.compute_display_name",
        return_value=Entry(
            id=entry_id,
            original_name="Updated Entry",
            translation="Translation originale",
            dictionary_id=1,
            display_name="Updated Entry (→ Translation originale)",
        ),
    ), patch("app.routes.entry.datetime") as mock_datetime:
        mock_now = datetime.now()
        mock_datetime.now.return_value = mock_now

        response = update_entry(
            request,
            entry_id=entry_id,
            entry_update=entry_update,
            session=mock_session,
        )

        assert response.id == entry_id
        assert response.original_name == "Updated Entry"
        assert response.translation == "Translation originale"
        assert response.dictionary_id == 1
        assert response.updated_at == mock_now


def test_update_entry_not_found():
    """Test that update_entry raises a 404 HTTPException when the entry is not found."""
    mock_session = MagicMock()

    entry_id = 999
    mock_session.get.return_value = None

    entry_update = EntryUpdate(original_name="Updated Entry")

    with pytest.raises(HTTPException) as excinfo:
        update_entry(
            request,
            entry_id=entry_id,
            entry_update=entry_update,
            session=mock_session,
        )

    assert excinfo.value.status_code == 404
    assert excinfo.value.detail == "Entry not found"
    mock_session.get.assert_called_once_with(Entry, entry_id)
    mock_session.add.assert_not_called()
    mock_session.commit.assert_not_called()
    mock_session.refresh.assert_not_called()


def test_update_entry_integrity_error():
    """Test that update_entry raises a 400 HTTPException when there's a duplicate entry."""
    mock_session = MagicMock()

    entry_id = 1
    mock_entry = Entry(
        id=entry_id,
        original_name="Original Entry",
        translation="Translation originale",
        dictionary_id=1,
    )

    mock_session.get.return_value = mock_entry
    mock_session.commit.side_effect = IntegrityError(
        "statement", "params", "orig"
    )

    entry_update = EntryUpdate(original_name="Duplicate Entry")

    with patch(
        "app.routes.entry.compute_display_name",
        return_value=mock_entry,
    ), patch("app.routes.entry.datetime") as mock_datetime:
        mock_datetime.now.return_value = datetime.now()

        with pytest.raises(HTTPException) as exc_info:
            update_entry(
                request,
                entry_id=entry_id,
                entry_update=entry_update,
                session=mock_session,
            )

        assert exc_info.value.status_code == 400
        assert (
            exc_info.value.detail
            == "An entry with this name already exists in this dictionary."
        )
        mock_session.get.assert_called_once_with(Entry, entry_id)
        mock_session.add.assert_called_once_with(mock_entry)
        mock_session.rollback.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_not_called()


def test_compute_display_name():
    """Test that compute_display_name returns the expected display name."""
    entry = Entry(
        original_name="Original Entry",
        translation="Translation originale",
        dictionary_id=1,
    )
    result = compute_display_name(entry)
    assert result.display_name == "Original Entry (Translation originale)"
