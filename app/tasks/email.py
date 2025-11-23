import logging

from jinja2 import Environment, FileSystemLoader

from app.core.email_client import api_instance, sib_api_v3_sdk

_logger = logging.getLogger(__name__)

env = Environment(loader=FileSystemLoader("app/templates"))  # NOSONAR


def render_email(template_name: str, **kwargs):
    """Render the email using Jinja."""
    template = env.get_template(template_name)
    return template.render(**kwargs)


def send_welcome_email(to: str, username: str):
    """Send an email."""
    subject = "Welcome to Lexit!"
    html_content = render_email("emails/welcome_email.html", username=username)

    email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": to}],
        sender={"email": "pro.cedricleroy@gmail.com", "name": "Lexit"},
        subject=subject,
        html_content=html_content,
    )

    try:
        response = api_instance.send_transac_email(email)
        _logger.info("Email sent: %s", response)
        return True
    except Exception as e:
        _logger.info("Error sending email: %s", e)
        raise e
