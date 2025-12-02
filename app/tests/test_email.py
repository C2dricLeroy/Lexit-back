from unittest.mock import MagicMock, patch

import pytest

from app.tasks.email import render_email, send_welcome_email


def test_render_email_renders_template():
    """Test render."""
    mock_template = MagicMock()
    mock_template.render.return_value = "<html>Welcome user!</html>"

    with patch(
        "app.tasks.email.env.get_template", return_value=mock_template
    ) as mock_get:
        result = render_email("emails/welcome_email.html", username="Alice")

    mock_get.assert_called_once_with("emails/welcome_email.html")

    mock_template.render.assert_called_once_with(username="Alice")

    assert result == "<html>Welcome user!</html>"


@patch("app.tasks.email.render_email", return_value="<html>Welcome!</html>")
@patch("app.tasks.email.api_instance.send_transac_email")
@patch("app.tasks.email._logger")
def test_send_welcome_email_success(mock_logger, mock_send, mock_render):
    """Test send welcome email succes."""
    mock_send.return_value = {"message": "success"}

    result = send_welcome_email("user@example.com", "Alice")

    mock_render.assert_called_once_with(
        "emails/welcome_email.html", username="Alice"
    )

    args, kwargs = mock_send.call_args
    sent_email = args[0]
    assert sent_email.subject == "Welcome to Lexit!"
    assert sent_email.to[0]["email"] == "user@example.com"
    assert sent_email.html_content == "<html>Welcome!</html>"

    assert result is True


@patch("app.tasks.email._logger")  # 1er argument
@patch("app.tasks.email.api_instance.send_transac_email")  # 2ème argument
@patch(
    "app.tasks.email.render_email",
    return_value="<html>Mocked Error Email!</html>",
)
def test_send_welcome_email_exception(mock_render, mock_send, mock_logger):
    """Test that send_welcome_email handles exceptions and logs the error, ensuring 'except' coverage."""
    raised_exception = Exception("SMTP failure")
    mock_send.side_effect = raised_exception
    with pytest.raises(Exception, match="SMTP failure"):
        send_welcome_email("user@example.com", "Alice")
    mock_logger.info.assert_called_once_with(
        "Error sending email: %s", raised_exception
    )
    mock_send.assert_called_once()
