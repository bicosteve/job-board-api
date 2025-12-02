import unittest
from unittest.mock import patch
from flask import Flask, json
from flask_restful import Api


from app.controllers.profile_controllers import (
    ProfileCreateController,
    ProfileGetController,
)


class TestProfileControllers(unittest.TestCase):
    def setUp(self):
        # Setup Flask app and test client
        self.app = Flask(__name__)
        api = Api(self.app)

        api.add_resource(ProfileCreateController, "/profile")
        api.add_resource(ProfileGetController, "/profile/get")

        self.client = self.app.test_client()

        self.valid_payload = {
            "first_name": "Steve",
            "last_name": "Tester",
            "bio": "QA Engineer",
        }
        self.headers = {"Authorization": "Bearer testtoken"}

    @patch("app.controllers.profile_controllers.ProfileService.create_profile")
    @patch("app.controllers.profile_controllers.ProfileSchema.load")
    def test_profile_create_success(self, mock_load, mock_create):
        mock_load.return_value = self.valid_payload
        mock_create.return_value = 1

        response = self.client.post(
            "/profile",
            data=json.dumps(self.valid_payload),
            headers=self.headers,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["msg"], "Profile created")

    @patch("app.controllers.profile_controllers.ProfileSchema.load")
    def test_profile_create_validation_error(self, mock_load):
        from marshmallow import ValidationError
        mock_load.side_effect = ValidationError(
            {"first_name": ["Missing data"]})

        response = self.client.post(
            "/profile",
            data=json.dumps(self.valid_payload),
            headers=self.headers,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("err", response.get_json())

    @patch("app.controllers.profile_controllers.ProfileService.create_profile")
    @patch("app.controllers.profile_controllers.ProfileSchema.load")
    def test_profile_create_failure(self, mock_load, mock_create):
        mock_load.return_value = self.valid_payload
        mock_create.return_value = 0  # simulate DB insert failure

        response = self.client.post(
            "/profile",
            data=json.dumps(self.valid_payload),
            headers=self.headers,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.get_json()[
                         "error"], "User profile was not created")

    def test_profile_create_missing_auth(self):
        response = self.client.post(
            "/profile",
            data=json.dumps(self.valid_payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)
        self.assertIn("validation_err", response.get_json())

    @patch("app.controllers.profile_controllers.ProfileService.get_profile")
    def test_profile_get_success(self, mock_get_profile):
        mock_get_profile.return_value = {
            "first_name": "Steve", "last_name": "Tester"}

        response = self.client.get("/profile/get", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("profile", response.get_json())
        self.assertEqual(response.get_json()["profile"]["first_name"], "Steve")

    @patch("app.controllers.profile_controllers.ProfileService.get_profile")
    def test_profile_get_not_found(self, mock_get_profile):
        mock_get_profile.return_value = None

        response = self.client.get("/profile/get", headers=self.headers)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json()["error"], "Profile not found")

    def test_profile_get_missing_auth(self):
        response = self.client.get("/profile/get")
        self.assertEqual(response.status_code, 401)
        self.assertIn("validation_err", response.get_json())
