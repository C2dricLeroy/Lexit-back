from app.core.email_client import api_instance, sib_api_v3_sdk


def send_email(to: str, subject: str, html_content: str):
    """Send an email."""
    email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": to}],
        sender={"email": "pro.cedricleroy@gmail.com", "name": "Lexit"},
        subject=subject,
        html_content=html_content,
    )

    try:
        response = api_instance.send_transac_email(email)
        print("Email sent:", response)
        return True
    except Exception as e:
        print("Error sending email:", e)
        raise e
