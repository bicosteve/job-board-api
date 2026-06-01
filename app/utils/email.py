import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

from .logger import Logger

load_dotenv()

SMTP_HOST = os.getenv("EMAIL_HOST", "")
SMTP_PORT = int(os.getenv("EMAIL_PORT", 587) or 587)
SMTP_USER = os.getenv("EMAIL_USER", "")
SMTP_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", os.getenv("CONTACT_EMAIL", "no-reply@example.com"))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True").lower() in ("true", "1", "yes")
EMAIL_USE_SSL = os.getenv("EMAIL_USE_SSL", "False").lower() in ("true", "1", "yes")


def send_email(to: str, subject: str, body: str) -> bool:
    if not SMTP_HOST:
        Logger.warn(f"Skipping email delivery to {to}: EMAIL_HOST is not configured")
        return False

    message = EmailMessage()
    message["From"] = EMAIL_FROM
    message["To"] = to
    message["Subject"] = subject
    message.set_content(body)

    try:
        if EMAIL_USE_SSL:
            smtp = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=10)
        else:
            smtp = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10)
            if EMAIL_USE_TLS:
                smtp.starttls()

        if SMTP_USER:
            smtp.login(SMTP_USER, SMTP_PASSWORD)

        smtp.send_message(message)
        smtp.quit()
        Logger.info(f"Email delivered to {to} subject={subject}")
        return True
    except Exception as exc:
        Logger.error(f"Failed to send email to {to}: {str(exc)}")
        return False
