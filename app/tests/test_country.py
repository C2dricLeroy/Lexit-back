from unittest.mock import MagicMock

from app.models.country import Country
from app.routes.country import get_country, get_country_by_id


def test_get_country():
    """Test that get_country returns all countries."""
    mock_session = MagicMock()

    mock_countries = [
        Country(
            id=1, name="France", code="FR", latitude=46.2276, longitude=2.2137
        ),
        Country(
            id=2,
            name="Germany",
            code="DE",
            latitude="51.1657",
            longitude="10.4515",
        ),
    ]

    mock_query_result = MagicMock()
    mock_query_result.all.return_value = mock_countries
    mock_session.exec.return_value = mock_query_result

    response = get_country(mock_session)

    assert response == mock_countries
    assert len(response) == 2
    assert response[0].name == "France"
    assert response[1].name == "Germany"
    mock_session.exec.assert_called_once()
    mock_query_result.all.assert_called_once()


def test_get_country_by_id_success():
    """Test that get_country_by_id returns a specific country when given a valid ID."""
    mock_session = MagicMock()

    mock_country = Country(
        id=1, name="France", code="FR", latitude="46.2276", longitude="2.2137"
    )

    mock_query_result = MagicMock()
    mock_query_result.first.return_value = mock_country
    mock_session.exec.return_value = mock_query_result

    response = get_country_by_id(country_id=1, session=mock_session)

    assert response == mock_country
    assert response.id == 1
    assert response.name == "France"
    assert response.code == "FR"
    assert response.latitude == "46.2276"
    assert response.longitude == "2.2137"
    mock_session.exec.assert_called_once()
    mock_query_result.first.assert_called_once()
