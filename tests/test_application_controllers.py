import unittest
from unittest.mock import patch
from flask import Flask, json
from flask_restful import Api

from app.controllers.application_controllers import (
    ApplicationsListController,
    ApplicationsCreateController,
    UsersJobApplicationsController,
    UsersJobApplicationController,
    ApplicationUpdateController,
)


class TestApplicationControllers(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        api = Api(self.app)

        api.add_resource(ApplicationsListController, "/applications")
        api.add_resource(ApplicationsCreateController, "/applications/create")
        api.add_resource(UsersJobApplicationsController, "/applications/user")
        api.add_resource(UsersJobApplicationController,
                         "/applications/<int:application_id>")
        api.add_resource(ApplicationUpdateController,
                         "/applications/<int:application_id>/update")

        self.client = self.app.test_client()
        self.headers = {"Authorization": "Bearer testtoken"}
        self.valid_payload = {"status": "Open"}

    # --- ApplicationsListController ---
    @patch("app.controllers.application_controllers.ApplicationService.get_all_job_applications")
    @patch("app.controllers.application_controllers.JobPaginaNationSchema.load")
    def test_list_applications_success(self, mock_load, mock_service):
        mock_load.return_value = {"page": 1, "limit": 10, "job_id": 1}
        mock_service.return_value = [{"id": 1, "applicant": "Steve"}]

        response = self.client.get("/applications?page=1&limit=10&job_id=1")
        self.assertEqual(response.status_code, 200)
        self.assertIn("info", response.get_json())

    # --- ApplicationsCreateController ---
    @patch("app.controllers.application_controllers.ApplicationService.make_application")
    @patch("app.controllers.application_controllers.JobApplicationSchema.load")
    def test_create_application_success(self, mock_load, mock_service):
        mock_load.return_value = {"job_id": 1,
                                  "cover_letter": "I am interested"}
        mock_service.return_value = 1

        response = self.client.post(
            "/applications/create",
            data=json.dumps({"job_id": 1, "cover_letter": "I am interested"}),
            headers=self.headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["msg"], "success")

    @patch("app.controllers.application_controllers.JobApplicationSchema.load")
    def test_create_application_validation_error(self, mock_load):
        from marshmallow import ValidationError
        mock_load.side_effect = ValidationError({"job_id": ["Missing data"]})

        response = self.client.post(
            "/applications/create",
            data=json.dumps({"cover_letter": "Missing job_id"}),
            headers=self.headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())

    # --- UsersJobApplicationsController ---
    @patch("app.controllers.application_controllers.ApplicationService.list_users_applications")
    def test_list_user_applications_success(self, mock_service):
        mock_service.return_value = [{"id": 1, "job": "QA Engineer"}]

        response = self.client.get("/applications/user", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("applications", response.get_json())

    # --- UsersJobApplicationController ---
    @patch("app.controllers.application_controllers.ApplicationService.get_job_application")
    @patch("app.controllers.application_controllers.ApplicationIdSchema.load")
    def test_get_user_application_success(self, mock_load, mock_service):
        mock_load.return_value = {"application_id": 1}
        mock_service.return_value = {"id": 1, "job": "QA Engineer"}

        response = self.client.get("/applications/1", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["job"], "QA Engineer")

    @patch("app.controllers.application_controllers.ApplicationService.get_job_application")
    @patch("app.controllers.application_controllers.ApplicationIdSchema.load")
    def test_get_user_application_not_found(self, mock_load, mock_service):
        mock_load.return_value = {"application_id": 999}
        mock_service.return_value = None

        response = self.client.get("/applications/999", headers=self.headers)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json()["msg"], "No application found")

    # --- ApplicationUpdateController ---
    @patch("app.controllers.application_controllers.ApplicationService.update_an_application")
    @patch("app.controllers.application_controllers.ApplicationIdSchema.load")
    @patch("app.controllers.application_controllers.JobUpdateSchema.load")
    def test_update_application_success(self, mock_load, mock_id_load, mock_service):
        mock_id_load.return_value = {"application_id": 1}
        mock_load.return_value = {"status": "Open"}
        mock_service.return_value = True

        response = self.client.put(
            "/applications/1/update",
            data=json.dumps({"status": "Open"}),
            headers=self.headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()[
                         "msg"], "Application update success")

    @patch("app.controllers.application_controllers.ApplicationService.update_an_application")
    @patch("app.controllers.application_controllers.ApplicationIdSchema.load")
    @patch("app.controllers.application_controllers.JobUpdateSchema.load")
    def test_update_application_not_found(self, mock_load, mock_id_load, mock_service):
        mock_id_load.return_value = {"application_id": 999}
        mock_load.return_value = {"status": "Closed"}
        mock_service.return_value = False

        response = self.client.put(
            "/applications/999/update",
            data=json.dumps({"status": "Closed"}),
            headers=self.headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn("Application 999 was not updated",
                      response.get_json()["msg"])
