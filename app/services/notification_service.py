import os
from typing import Optional

from flask import current_app

from ..utils.mails import Mails

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

APPLICATION_STATUS_LABELS = {
    1: "Submitted",
    2: "In review",
    3: "Interview",
    4: "Decision",
}


def _subject(role: str, topic: str) -> str:
    return f"{role}: {topic}"


def _friendly_status(status: int) -> str:
    return APPLICATION_STATUS_LABELS.get(status, str(status))


class NotificationService:
    @staticmethod
    def send_verification_code(email: str, code: str, is_admin: bool = False) -> bool:
        role = "Employer" if is_admin else "Candidate"
        subject = _subject(role, "Verify your account")
        body = (
            f"Hi,\n\nYour {role.lower()} account is almost ready."
            f"\nUse the verification code below to complete registration:\n\n{code}\n\n"
            "If you did not request this, ignore this email.\n\n"
            f"Thank you,\n{role} team"
        )

        Mails.send_mail_task.delay(
            current_app.config["EMAIL_FROM"],
            email,
            subject,
            body,
        )

        return True

    @staticmethod
    def send_password_reset(email: str, token: str) -> bool:
        reset_url = f"{FRONTEND_URL}/reset-password?token={token}"
        subject = _subject("Candidate", "Reset your password")
        body = (
            f"Hi,\n\nWe received a request to reset your password."
            f"\nClick the link below or paste it into your browser:\n\n{reset_url}\n\n"
            "If you did not request a password reset, you can safely ignore this email.\n\n"
            "Thanks,\nCandidate support"
        )

        Mails.send_mail_task.delay(
            current_app.config["EMAIL_FROM"],
            email,
            subject,
            body,
        )

        return True

    @staticmethod
    def notify_applicant_of_submission(
        email: str, job_title: str, company_name: str
    ) -> bool:
        subject = _subject("Candidate", "Your application is received")
        body = (
            f"Hi,\n\nYour application for '{job_title}' at {company_name} has been received."
            "\nWe will notify you when your hiring status changes.\n\n"
            "Track progress from your dashboard.\n\nBest,\nRecruiting team"
        )

        Mails.send_mail_task.delay(
            current_app.config["EMAIL_FROM"],
            email,
            subject,
            body,
        )

        return True

    @staticmethod
    def notify_employer_of_new_application(
        email: str, job_title: str, applicant_email: str
    ) -> bool:
        subject = _subject("Employer", "New candidate application")
        body = (
            f"Hi,\n\nA new application has been submitted for '{job_title}' by {applicant_email}."
            "\nReview the application and update the status from your employer dashboard.\n\nBest,\nRecruiting platform"
        )

        Mails.send_mail_task.delay(
            current_app.config["EMAIL_FROM"],
            email,
            subject,
            body,
        )

        return True

    @staticmethod
    def notify_applicant_status_change(
        email: str, job_title: str, status: int, company_name: Optional[str] = None
    ) -> bool:
        status_label = _friendly_status(status)
        company_label = f" at {company_name}" if company_name else ""
        subject = _subject("Candidate", "Application status updated")
        body = (
            f"Hi,\n\nThe status of your application for '{job_title}'{company_label}"
            f"has changed to '{status_label}'.\n\n"
            "You can view the latest updates in your dashboard.\n\nBest,\nRecruiting team"
        )

        Mails.send_mail_task.delay(
            current_app.config["EMAIL_FROM"],
            email,
            subject,
            body,
        )

        return True
