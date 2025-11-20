from app.core.email_client import api_instance, sib_api_v3_sdk


def send_welcome_email(to: str):
    """Send an email."""
    subject = "Welcome to Lexit!"
    html_content = """
    <h1>Welcome!</h1>
    <p>Thanks for signing up to Lexit.</p>
    """

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
