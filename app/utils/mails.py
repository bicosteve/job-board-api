import requests
from flask import current_app
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from ..extensions.celery import celery
from .logger import Logger


class Mails:

    @staticmethod
    def send_by_sendgrid(
        mail_from: str,
        mail_to: str,
        subject: str,
        content: str,
    ):
        message = Mail(
            from_email=mail_from,
            to_emails=mail_to,
            subject=subject,
            html_content=f"<strong>{content}</strong>",
        )

        try:
            sg = SendGridAPIClient(current_app.config["SENDGRID_API_KEY"])
            response = sg.send(message)
            Logger.info(f"Message sent successfully to {mail_to}")
            return {"status_code": response.status_code, "to": mail_to}
        except Exception as e:
            Logger.warn(f"Failed to send mail to {mail_to} because of {str(e)}")
            raise e

    @staticmethod
    def send_by_mailgun(mail_from, mail_to, subject, content, content_type):
        domain = current_app.config["MAILGUN_DOMAIN"]
        api_key = current_app.config["MAILGUN_API_KEY"]
        base_url = current_app.config["MAILGUN_BASE_URL"]

        data = {
            "from": mail_from,
            "to": mail_to,
            "subject": subject,
            "text": content,
        }

        if content_type == "text/html":
            data["html"] = content
        else:
            data["text"] = content

        try:
            response = requests.post(
                f"{base_url}/{domain}/messages",
                auth=("api", api_key),
                data=data,
                timeout=10,
            )

            response.raise_for_status()
            Logger.info(f"Message sent successfully to {mail_to}")
            return {
                "status_code": response.status_code,
                "to": mail_to,
                "body": response.json(),
            }
        except requests.exceptions.RequestException as e:
            Logger.warn(f"Failed to send mail to {mail_to} because of {str(e)}")
            raise e

    @staticmethod
    @celery.task(max_retries=3, default_retry_delay=60)
    def send_mail_task(
        email_from: str,
        email_to: str,
        subject: str,
        content: str,
    ):
        try:
            Mails.send_by_mailgun(
                mail_from=email_from,
                mail_to=email_to,
                subject=subject,
                content=content,
                content_type="text/html",
            )
        except Exception as exc:
            raise exc
