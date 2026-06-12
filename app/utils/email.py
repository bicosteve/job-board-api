import os
import smtplib
from email.message import EmailMessage

from celery import Celery
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from .logger import Logger

load_dotenv()

SMTP_HOST = os.getenv("EMAIL_HOST", "")
SMTP_PORT = int(os.getenv("EMAIL_PORT", 587) or 587)
SMTP_USER = os.getenv("EMAIL_USER", "")
SMTP_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", os.getenv("CONTACT_EMAIL", "no-reply@example.com"))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True").lower() in ("true", "1", "yes")
EMAIL_USE_SSL = os.getenv("EMAIL_USE_SSL", "False").lower() in ("true", "1", "yes")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
REDIS_URL = (
    f'{os.getenv("REDIS_HOST")}:{os.getenv('REDIS_PORT')}/{os.getenv('REDIS_DB')}'
)

celery = Celery(__name__, broker=REDIS_URL)


class Mails:

    @staticmethod
    def send_email(to: str, subject: str, body: str) -> bool:
        if not SMTP_HOST:
            Logger.warn(
                f"Skipping email delivery to {to}: EMAIL_HOST is not configured"
            )
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

    @staticmethod
    def send_by_sendgrid(mail_from: str, mail_to: str, subject: str, content: str):
        message = Mail(
            from_email=mail_from,
            to_emails=mail_to,
            subject=subject,
            html_content=content,
        )

        try:
            sg = SendGridAPIClient(SENDGRID_API_KEY)
            response = sg.send(message)
            return response.status_code
        except Exception as e:
            print(str(e))

    @staticmethod
    @celery.task
    def send_mail_task(
        email_from: str,
        email_to: str,
        content: str,
        subject: str = "",
    ):
        Mails.send_by_sendgrid(email_from, email_to, subject, content)
        Mails.send_email(email_to, subject, content)
