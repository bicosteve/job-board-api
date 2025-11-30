import unittest
from unittest.mock import patch
from flask import Flask, json
from flask_restful import Api

# Import your controllers
from app.controllers.job_controllers import (
    PostJobController,
    JobsListController,
    JobObjectController,
    ModifyJobObjectController,
)


class JobControllerTestCase(unittest.TestCase):
    def setUp(self):
        # Setup Flask app and test client
        self.app = Flask(__name__)
        api = Api(self.app)

        api.add_resource(PostJobController, "/jobs")
        api.add_resource(JobsListController, "/jobs/list")
        api.add_resource(JobObjectController, "/jobs/<int:job_id>")
        api.add_resource(ModifyJobObjectController,
                         "/jobs/<int:job_id>/update")

        self.client = self.app.test_client()

        self.payload = {
            "title": "QA Engineer",
            "details": {
                "description": "Testing APIs",
                "requirements": "Python, Flask",
                "location": "Nairobi",
                "employment_type": "Full time",
                "salary_range": "1000-2000 USD",
                "deadline": "2025-12-31",
                "status": "Open",
                "company_name": "Shade Limited",
                "application_url": "https://example.com/apply"
            }
        }

        self.update_payload = {
            "title": "Updated Job",
            "description": "This is a valid description",
            "requirements": "Python, Flask",
            "location": "Nairobi",
            "employment_type": "Full time",
            "salary_range": "1000-2000 USD",
            "deadline": "2025-12-31",
            "status": "Open",
            "company_name": "Shade Limited",
            "application_url": "https://example.com/apply"
        }

    @patch("app.controllers.job_controllers.JobService.add_job")
    def test_post_job_success(self, mock_add_job):
        mock_add_job.return_value = 123
        headers = {"Authorization": "Bearer testtoken"}

        response = self.client.post(
            "/jobs",
            data=json.dumps(self.payload),
            headers=headers,
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data["msg"], "job created")

    def test_post_job_missing_auth(self):
        payload = {"title": "QA Engineer",
                   "details": {"description": "Testing"}}
        response = self.client.post(
            "/jobs",
            data=json.dumps(self.payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)
        self.assertIn("validation_err", response.get_json())

    @patch("app.controllers.job_controllers.JobService.fetch_jobs")
    def test_get_jobs_list_success(self, mock_fetch_jobs):
        mock_fetch_jobs.return_value = [{"id": 1, "title": "QA Engineer"}]

        response = self.client.get("/jobs/list?page=1&limit=10")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("result", data)
        self.assertEqual(data["result"][0]["title"], "QA Engineer")

    @patch("app.controllers.job_controllers.JobService.fetch_job")
    def test_get_job_object_not_found(self, mock_fetch_job):
        mock_fetch_job.return_value = None
        response = self.client.get("/jobs/999")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json()["message"], "Job not found")

    @patch("app.controllers.job_controllers.JobService.update_job")
    def test_put_job_update_success(self, mock_update_job):
        mock_update_job.return_value = {"id": 1, "title": "Updated Job"}
        headers = {"Authorization": "Bearer testtoken"}
        payload = {"title": "Updated Job"}

        response = self.client.put(
            "/jobs/1/update",
            data=json.dumps(self.update_payload),
            headers=headers,
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["title"], "Updated Job")

    @patch("app.controllers.job_controllers.JobService.update_job")
    def test_put_job_update_not_found(self, mock_update_job):
        mock_update_job.return_value = None
        headers = {"Authorization": "Bearer testtoken"}

        response = self.client.put(
            "/jobs/1/update",
            data=json.dumps(self.update_payload),
            headers=headers,
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json()["msg"], "error job not found")
