import unittest
from unittest.mock import patch
from app.services.application_service import ApplicationService
from app.utils.exceptions import GenericDatabaseError


class TestApplicationService(unittest.TestCase):
    def setUp(self):
        self.token = "validtoken"
        self.decoded = {"profile_id": 1}
        self.payload = {"job_id": 1, "status": 1,
                        "cover_letter": "Hi", "resume_url": "url"}

    # --- make_application ---
    @patch("app.services.application_service.ApplicationRepository.create_application")
    @patch("app.services.application_service.Security.decode_jwt_token")
    def test_make_application_success(self, mock_decode, mock_create):
        mock_decode.return_value = self.decoded
        mock_create.return_value = 1
        result = ApplicationService.make_application(self.token, self.payload)
        self.assertTrue(result)

    @patch("app.services.application_service.Security.decode_jwt_token")
    def test_make_application_invalid_token(self, mock_decode):
        mock_decode.return_value = None
        with self.assertRaises(GenericDatabaseError):
            ApplicationService.make_application(self.token, self.payload)

    @patch("app.services.application_service.Security.decode_jwt_token")
    def test_make_application_missing_user_id(self, mock_decode):
        mock_decode.return_value = {"profile_id": None}
        with self.assertRaises(GenericDatabaseError):
            ApplicationService.make_application(self.token, self.payload)

    def test_make_application_invalid_payload_type(self):
        with self.assertRaises(GenericDatabaseError):
            ApplicationService.make_application(self.token, ["not_a_dict"])

    # --- get_all_job_applications ---
    @patch("app.services.application_service.ApplicationRepository.get_jobs_applications")
    def test_get_all_job_applications_success(self, mock_get_jobs):
        mock_get_jobs.return_value = [{"id": 1}]
        result = ApplicationService.get_all_job_applications(1, 10, 1)
        self.assertEqual(result["page"], 1)
        self.assertEqual(result["limit"], 10)
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["applications"][0]["id"], 1)

    @patch("app.services.application_service.ApplicationRepository.get_jobs_applications")
    def test_get_all_job_applications_error(self, mock_get_jobs):
        mock_get_jobs.side_effect = Exception("DB error")
        with self.assertRaises(GenericDatabaseError):
            ApplicationService.get_all_job_applications(1, 10, 1)

    # --- get_job_application ---
    @patch("app.services.application_service.ApplicationRepository.get_user_application")
    @patch("app.services.application_service.Security.decode_jwt_token")
    def test_get_job_application_success(self, mock_decode, mock_get_user_app):
        mock_decode.return_value = self.decoded
        mock_get_user_app.return_value = {"id": 1}
        result = ApplicationService.get_job_application(self.token, 1)
        self.assertEqual(result["id"], 1)

    @patch("app.services.application_service.Security.decode_jwt_token")
    def test_get_job_application_invalid_token(self, mock_decode):
        mock_decode.return_value = None
        with self.assertRaises(GenericDatabaseError):
            ApplicationService.get_job_application(self.token, 1)

    # --- list_users_applications ---
    @patch("app.services.application_service.ApplicationRepository.get_user_applications")
    @patch("app.services.application_service.Security.decode_jwt_token")
    def test_list_users_applications_success(self, mock_decode, mock_get_apps):
        mock_decode.return_value = self.decoded
        mock_get_apps.return_value = [{"id": 1}]
        result = ApplicationService.list_users_applications(self.token)
        self.assertEqual(result[0]["id"], 1)

    @patch("app.services.application_service.Security.decode_jwt_token")
    def test_list_users_applications_invalid_token(self, mock_decode):
        mock_decode.return_value = None
        with self.assertRaises(GenericDatabaseError):
            ApplicationService.list_users_applications(self.token)

    # --- update_an_application ---
    @patch("app.services.application_service.ApplicationRepository.update_application")
    @patch("app.services.application_service.Security.decode_jwt_token")
    def test_update_an_application_success(self, mock_decode, mock_update):
        mock_decode.return_value = self.decoded
        mock_update.return_value = 1
        result = ApplicationService.update_an_application(self.token, 1, 2)
        self.assertTrue(result)

    @patch("app.services.application_service.Security.decode_jwt_token")
    def test_update_an_application_invalid_token(self, mock_decode):
        mock_decode.return_value = None
        with self.assertRaises(GenericDatabaseError):
            ApplicationService.update_an_application(self.token, 1, 2)
