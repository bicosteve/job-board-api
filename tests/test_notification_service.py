import unittest
from unittest.mock import MagicMock, patch

from flask import Flask

from app.services.notification_service import NotificationService


class TestNotificationService(unittest.TestCase):
    """Unit tests for NotificationService.

    The service relies on Flask's `current_app` for the sender email and uses
    the Celery task `Mails.send_mail_task.delay` to enqueue outbound emails.
    These tests push a real Flask application context (so `current_app` works
    normally) and patch only the celery task to assert on enqueue behaviour.
    """

    def setUp(self):
        # A minimal Flask app gives us a working `current_app` proxy.
        self.app = Flask(__name__)
        self.app.config["EMAIL_FROM"] = "no-reply@jobboard.test"
        self.app_context = self.app.app_context()
        self.app_context.push()

        self.email = "user@example.com"
        self.code = "654321"
        self.token = "reset-token-abc"
        self.job_title = "Backend Engineer"
        self.company_name = "Acme Corp"
        self.applicant_email = "applicant@example.com"
        self.status = 2  # "In review"
        self.sender = self.app.config["EMAIL_FROM"]

        # Patch the celery task used by the service.
        self.mail_patcher = patch(
            "app.services.notification_service.Mails.send_mail_task"
        )
        self.mock_mail_task = self.mail_patcher.start()
        self.mock_mail_task.delay = MagicMock()

        self.addCleanup(self.mail_patcher.stop)
        self.addCleanup(self.app_context.pop)

    # ---------- send_verification_code ----------
    def test_send_verification_code_candidate(self):
        """Candidate verification email is enqueued with correct subject and body."""
        result = NotificationService.send_verification_code(
            self.email, self.code, is_admin=False
        )

        self.assertTrue(result)
        self.mock_mail_task.delay.assert_called_once()
        args = self.mock_mail_task.delay.call_args[0]
        self.assertEqual(args[0], self.sender)
        self.assertEqual(args[1], self.email)
        self.assertIn("Candidate: Verify your account", args[2])
        self.assertIn(self.code, args[3])
        self.assertIn("candidate", args[3].lower())

    def test_send_verification_code_admin(self):
        """Admin verification email uses the Employer role label."""
        result = NotificationService.send_verification_code(
            self.email, self.code, is_admin=True
        )

        self.assertTrue(result)
        self.mock_mail_task.delay.assert_called_once()
        args = self.mock_mail_task.delay.call_args[0]
        self.assertIn("Employer: Verify your account", args[2])
        self.assertIn("employer", args[3].lower())

    # ---------- send_password_reset ----------
    def test_send_password_reset_includes_reset_url(self):
        """Password reset email contains a reset URL with the token."""
        result = NotificationService.send_password_reset(
            self.email, self.token)

        self.assertTrue(result)
        self.mock_mail_task.delay.assert_called_once()
        args = self.mock_mail_task.delay.call_args[0]
        self.assertIn("Candidate: Reset your password", args[2])
        self.assertIn("reset-password", args[3])
        self.assertIn(self.token, args[3])

    # ---------- notify_applicant_of_submission ----------
    def test_notify_applicant_of_submission(self):
        """Submission email references the job title and company name."""
        result = NotificationService.notify_applicant_of_submission(
            self.email, self.job_title, self.company_name
        )

        self.assertTrue(result)
        self.mock_mail_task.delay.assert_called_once()
        args = self.mock_mail_task.delay.call_args[0]
        self.assertIn("Candidate: Your application is received", args[2])
        self.assertIn(self.job_title, args[3])
        self.assertIn(self.company_name, args[3])

    # ---------- notify_employer_of_new_application ----------
    def test_notify_employer_of_new_application(self):
        """Employer email mentions applicant email and job title."""
        result = NotificationService.notify_employer_of_new_application(
            self.email, self.job_title, self.applicant_email
        )

        self.assertTrue(result)
        self.mock_mail_task.delay.assert_called_once()
        args = self.mock_mail_task.delay.call_args[0]
        self.assertIn("Employer: New candidate application", args[2])
        self.assertIn(self.applicant_email, args[3])
        self.assertIn(self.job_title, args[3])

    # ---------- notify_applicant_status_change ----------
    def test_notify_applicant_status_change_with_company(self):
        """Status change email uses friendly status label and company name."""
        result = NotificationService.notify_applicant_status_change(
            self.email, self.job_title, self.status, self.company_name
        )

        self.assertTrue(result)
        self.mock_mail_task.delay.assert_called_once()
        args = self.mock_mail_task.delay.call_args[0]
        self.assertIn("Candidate: Application status updated", args[2])
        self.assertIn(self.job_title, args[3])
        self.assertIn(self.company_name, args[3])
        # APPLICATION_STATUS_LABELS[2] == "In review"
        self.assertIn("In review", args[3])

    def test_notify_applicant_status_change_without_company(self):
        """Status change email handles missing company name gracefully."""
        result = NotificationService.notify_applicant_status_change(
            self.email, self.job_title, self.status, company_name=None
        )

        self.assertTrue(result)
        args = self.mock_mail_task.delay.call_args[0]
        # Should not have " at " when no company name provided
        self.assertNotIn(" at  ", args[3])
        self.assertIn(self.job_title, args[3])

    def test_notify_applicant_status_change_unknown_status(self):
        """Unknown status codes fall back to the raw status string."""
        result = NotificationService.notify_applicant_status_change(
            self.email, self.job_title, 999
        )

        self.assertTrue(result)
        args = self.mock_mail_task.delay.call_args[0]
        # Unknown status should be converted to its string repr
        self.assertIn("999", args[3])

    def test_all_methods_return_true_on_success(self):
        """All public methods should return True when enqueue succeeds."""
        self.assertTrue(
            NotificationService.send_verification_code(
                self.email, self.code, is_admin=False
            )
        )
        self.assertTrue(
            NotificationService.send_verification_code(
                self.email, self.code, is_admin=True
            )
        )
        self.assertTrue(NotificationService.send_password_reset(
            self.email, self.token))
        self.assertTrue(
            NotificationService.notify_applicant_of_submission(
                self.email, self.job_title, self.company_name
            )
        )
        self.assertTrue(
            NotificationService.notify_employer_of_new_application(
                self.email, self.job_title, self.applicant_email
            )
        )
        self.assertTrue(
            NotificationService.notify_applicant_status_change(
                self.email, self.job_title, self.status, self.company_name
            )
        )
        # Six successful calls, one per public method invocation.
        self.assertEqual(self.mock_mail_task.delay.call_count, 6)


if __name__ == "__main__":
    unittest.main()
