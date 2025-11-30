import unittest
from unittest.mock import patch, MagicMock
from app.services.job_service import JobService
from app.utils.exceptions import GenericDatabaseError, InvalidLoginAttemptError


class TestJobService(unittest.TestCase):

    @patch("app.services.job_service.JobRepository.insert_job")
    @patch("app.services.job_service.Security.decode_jwt_token")
    def test_add_job_success(self, mock_decode, mock_insert):
        mock_decode.return_value = {
            "profile_id": 1, "email": "admin@example.com"}
        mock_insert.return_value = 10

        data = {
            "title": "QA Engineer",
            "description": "Testing APIs",
            "token": "validtoken"
        }

        result = JobService.add_job(data)
        self.assertEqual(result, 10)
        self.assertEqual(data["admin_id"], 1)

    @patch("app.services.job_service.Security.decode_jwt_token")
    def test_add_job_invalid_token(self, mock_decode):
        mock_decode.return_value = {
            "profile_id": None, "email": "admin@example.com"}
        data = {"title": "QA Engineer",
                "description": "Testing APIs", "token": "badtoken"}

        with self.assertRaises(GenericDatabaseError):
            JobService.add_job(data)

    @patch("app.services.job_service.JobRepository.insert_job")
    @patch("app.services.job_service.Security.decode_jwt_token")
    def test_add_job_insert_failure(self, mock_decode, mock_insert):
        mock_decode.return_value = {
            "profile_id": 1, "email": "admin@example.com"}
        mock_insert.return_value = None
        data = {"title": "QA Engineer",
                "description": "Testing APIs", "token": "validtoken"}

        result = JobService.add_job(data)
        self.assertIsNone(result)

    @patch("app.services.job_service.JobRepository.get_jobs")
    def test_fetch_jobs_success(self, mock_get_jobs):
        mock_get_jobs.return_value = [{"id": 1, "title": "QA Engineer"}]

        result = JobService.fetch_jobs(page=1, limit=10)
        self.assertEqual(result["page"], 1)
        self.assertEqual(result["limit"], 10)
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["jobs"][0]["title"], "QA Engineer")

    @patch("app.services.job_service.JobRepository.get_job")
    def test_fetch_job_success(self, mock_get_job):
        mock_get_job.return_value = {"id": 1, "title": "QA Engineer"}
        result = JobService.fetch_job(1)
        self.assertEqual(result["title"], "QA Engineer")

    @patch("app.services.job_service.JobRepository.update_job")
    @patch("app.services.job_service.JobRepository.get_job")
    @patch("app.services.job_service.Security.decode_jwt_token")
    def test_update_job_success(self, mock_decode, mock_get_job, mock_update_job):
        mock_decode.return_value = {
            "profile_id": 1, "email": "admin@example.com"}
        mock_update_job.return_value = 1
        mock_get_job.return_value = {"id": 1, "title": "Updated Job"}

        result = JobService.update_job(
            1, "validtoken", {"title": "Updated Job"})
        self.assertEqual(result["title"], "Updated Job")

    @patch("app.services.job_service.Security.decode_jwt_token")
    def test_update_job_invalid_token(self, mock_decode):
        mock_decode.return_value = {
            "profile_id": None, "email": "admin@example.com"}
        with self.assertRaises(GenericDatabaseError):
            JobService.update_job(1, "badtoken", {"title": "Updated Job"})

    @patch("app.services.job_service.JobRepository.update_job")
    @patch("app.services.job_service.Security.decode_jwt_token")
    def test_update_job_not_found(self, mock_decode, mock_update_job):
        mock_decode.return_value = {
            "profile_id": 1, "email": "admin@example.com"}
        mock_update_job.return_value = 0

        with self.assertRaises(GenericDatabaseError):
            JobService.update_job(999, "validtoken", {"title": "Updated Job"})
