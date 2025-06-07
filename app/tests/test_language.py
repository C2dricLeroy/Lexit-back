from unittest.mock import MagicMock, patch

from starlette.requests import Request

from app.dto.language import LanguageCreate
from app.models.language import Language
from app.routes.language import (
    create_language,
    get_language_by_id,
    get_languages,
)

fake_scope = {
    "type": "http",
    "path": "/",
    "headers": [],
    "client": ("127.0.0.1", 12345),
    "method": "GET",
}

request = Request(scope=fake_scope)


def test_get_languages_empty():
    """Test retrieving languages when none exist."""
    mock_session = MagicMock()

    mock_query_result = MagicMock()
    mock_query_result.all.return_value = []
    mock_session.exec.return_value = mock_query_result

    result = get_languages(request, mock_session)

    assert result == []
    assert len(result) == 0
    mock_session.exec.assert_called_once()
    mock_query_result.all.assert_called_once()


def test_get_languages_with_multiple_languages():
    """Test retrieving languages when multiple languages exist."""
    mock_session = MagicMock()

    mock_languages = [
        Language(id=1, name="English", code="en"),
        Language(id=2, name="French", code="fr"),
        Language(id=3, name="Spanish", code="es"),
    ]

    mock_query_result = MagicMock()
    mock_query_result.all.return_value = mock_languages
    mock_session.exec.return_value = mock_query_result

    result = get_languages(request, mock_session)

    assert result == mock_languages
    assert len(result) == 3
    assert result[0].name == "English"
    assert result[1].name == "French"
    assert result[2].name == "Spanish"
    mock_session.exec.assert_called_once()
    mock_query_result.all.assert_called_once()


def test_get_language_by_id_success():
    """Test retrieving a language by its valid ID returns the correct language."""
    mock_session = MagicMock()

    mock_language = Language(id=1, name="English", code="en")

    mock_query_result = MagicMock()
    mock_query_result.first.return_value = mock_language
    mock_session.exec.return_value = mock_query_result

    result = get_language_by_id(request, language_id=1, session=mock_session)

    assert result == mock_language
    assert result.id == 1
    assert result.name == "English"
    assert result.code == "en"
    mock_session.exec.assert_called_once()
    mock_query_result.first.assert_called_once()


def test_create_language_success():
    """Test creating a new language with valid data returns the created language."""
    mock_session = MagicMock()

    language_data = LanguageCreate(name="German", code="de")

    db_language = Language(id=4, name="German", code="de")

    # Mock the behavior of adding to the database
    mock_session.add.return_value = None
    mock_session.commit.return_value = None
    mock_session.refresh.side_effect = lambda x: setattr(x, "id", 4)

    with patch("app.routes.language.Language", return_value=db_language):
        result = create_language(request, language_data, mock_session)

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0] == db_language
    assert result[0].id == 4
    assert result[0].name == "German"
    assert result[0].code == "de"
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()
