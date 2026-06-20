import unittest
from datetime import datetime
from unittest.mock import patch

from flask import Flask

from app.controllers.user_controllers import (
    CheckAppHealthController,
    RequestUserPasswordResetController,
    ResetUserPasswordController,
    UserProfileController,
    VerifyUserAccountController,
)
from app.utils.exceptions import GenericDatabaseError, UserExistError


class TestCheckAppHealthController(unittest.TestCase):
    """Tests for the simple health-check endpoint."""

    def setUp(self):
        self.app = Flask(__name__)
        self.client = self.app.test_client()
        self.app.add_url_rule(
            "/health",
            view_func=CheckAppHealthController.as_view("health"),
        )

    def test_health_returns_running_message(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)

        body = response.get_json()
        self.assertIn("data", body)
        data = body["data"]
        self.assertEqual(data["msg"], "App is running successfully")
        self.assertIn("now", data)
        self.assertIn("date", data)
        self.assertIn("time", data)

        # Confirm the timestamp string is parseable.
        datetime.strptime(data["now"], "%Y-%m-%d %H:%M:%S")


class TestUserProfileController(unittest.TestCase):
    """Tests for the protected /user endpoint."""

    def setUp(self):
        self.app = Flask(__name__)
        self.client = self.app.test_client()
        self.app.add_url_rule("/user", view_func=UserProfileController.as_view("user"))
        self.headers = {"Authorization": "Bearer validtoken"}
        self.user_payload = {
            "user_id": 1,
            "email": "user@example.com",
            "status": 1,
            "reset_token": None,
            "created_at": "2025-01-01 12:00:00",
            "updated_at": "2025-01-02 12:00:00",
        }

    def test_user_profile_missing_authorization_header(self):
        response = self.client.get("/user")
        self.assertEqual(response.status_code, 401)
        self.assertIn("error", response.get_json())

    def test_user_profile_invalid_authorization_header(self):
        response = self.client.get("/user", headers={"Authorization": "Basic abc"})
        self.assertEqual(response.status_code, 401)
        self.assertIn("error", response.get_json())

    @patch("app.controllers.user_controllers.UserService.get_user_profile")
    @patch("app.controllers.user_controllers.Security.decode_jwt_token")
    def test_user_profile_success(self, mock_decode, mock_get_user_profile):
        mock_decode.return_value = {"profile_id": 1, "email": "user@example.com"}
        mock_get_user_profile.return_value = self.user_payload

        response = self.client.get("/user", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertEqual(body["email"], self.user_payload["email"])
        self.assertEqual(body["user_id"], self.user_payload["user_id"])
        mock_decode.assert_called_once_with("validtoken")
        mock_get_user_profile.assert_called_once_with(1)

    @patch("app.controllers.user_controllers.Security.decode_jwt_token")
    def test_user_profile_token_missing_profile_id(self, mock_decode):
        mock_decode.return_value = {"email": "user@example.com"}

        response = self.client.get("/user", headers=self.headers)
        self.assertEqual(response.status_code, 401)
        self.assertIn("error", response.get_json())

    @patch("app.controllers.user_controllers.UserService.get_user_profile")
    @patch("app.controllers.user_controllers.Security.decode_jwt_token")
    def test_user_profile_not_found(self, mock_decode, mock_get_user_profile):
        mock_decode.return_value = {"profile_id": 99}
        mock_get_user_profile.return_value = None

        response = self.client.get("/user", headers=self.headers)
        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.get_json())

    @patch("app.controllers.user_controllers.UserService.get_user_profile")
    @patch("app.controllers.user_controllers.Security.decode_jwt_token")
    def test_user_profile_expired_token(self, mock_decode, mock_get_user_profile):
        from jwt import ExpiredSignatureError

        mock_decode.side_effect = ExpiredSignatureError("expired")

        response = self.client.get("/user", headers=self.headers)
        self.assertEqual(response.status_code, 401)
        self.assertIn("error", response.get_json())

    @patch("app.controllers.user_controllers.UserService.get_user_profile")
    @patch("app.controllers.user_controllers.Security.decode_jwt_token")
    def test_user_profile_invalid_token(self, mock_decode, mock_get_user_profile):
        from jwt import InvalidTokenError

        mock_decode.side_effect = InvalidTokenError("bad")

        response = self.client.get("/user", headers=self.headers)
        self.assertEqual(response.status_code, 401)
        self.assertIn("error", response.get_json())

    @patch("app.controllers.user_controllers.UserService.get_user_profile")
    @patch("app.controllers.user_controllers.Security.decode_jwt_token")
    def test_user_profile_unexpected_error(self, mock_decode, mock_get_user_profile):
        mock_decode.side_effect = Exception("boom")

        response = self.client.get("/user", headers=self.headers)
        self.assertEqual(response.status_code, 500)
        self.assertIn("error", response.get_json())


class TestVerifyUserAccountController(unittest.TestCase):
    """Tests for the account verification endpoint."""

    def setUp(self):
        self.app = Flask(__name__)
        self.client = self.app.test_client()
        self.app.add_url_rule(
            "/verify",
            view_func=VerifyUserAccountController.as_view("verify"),
        )
        self.email = "user@example.com"
        self.code = "123456"
        self.payload = {"email": self.email, "verification_code": self.code}

    @patch("app.controllers.user_controllers.UserService.verify_account")
    def test_verify_account_success(self, mock_verify):
        mock_verify.return_value = True

        response = self.client.post("/verify", json=self.payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["msg"], "account verification success")
        mock_verify.assert_called_once_with(self.email, self.code)

    @patch("app.controllers.user_controllers.UserService.verify_account")
    def test_verify_account_returns_false(self, mock_verify):
        mock_verify.return_value = False

        response = self.client.post("/verify", json=self.payload)
        self.assertEqual(response.status_code, 500)
        self.assertIn("error", response.get_json())

    def test_verify_account_validation_error(self):
        from marshmallow import ValidationError

        with patch.object(
            VerifyUserAccountController.verify_account_schema,
            "load",
            side_effect=ValidationError("bad data"),
        ):
            response = self.client.post("/verify", json={})
            self.assertEqual(response.status_code, 400)
            self.assertIn("validation_error", response.get_json())

    @patch("app.controllers.user_controllers.UserService.verify_account")
    def test_verify_account_user_exist_error(self, mock_verify):
        mock_verify.side_effect = UserExistError("user exists")

        response = self.client.post("/verify", json=self.payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("user_error", response.get_json())

    @patch("app.controllers.user_controllers.UserService.verify_account")
    def test_verify_account_database_error(self, mock_verify):
        mock_verify.side_effect = GenericDatabaseError("db failed")

        response = self.client.post("/verify", json=self.payload)
        self.assertEqual(response.status_code, 500)
        self.assertIn("db_error", response.get_json())

    @patch("app.controllers.user_controllers.UserService.verify_account")
    def test_verify_account_unexpected_error(self, mock_verify):
        mock_verify.side_effect = Exception("kaboom")

        response = self.client.post("/verify", json=self.payload)
        self.assertEqual(response.status_code, 500)
        self.assertIn("generic_error", response.get_json())


class TestRequestUserPasswordResetController(unittest.TestCase):
    """Tests for the request-reset-code endpoint."""

    def setUp(self):
        self.app = Flask(__name__)
        self.client = self.app.test_client()
        self.app.add_url_rule(
            "/request-reset",
            view_func=RequestUserPasswordResetController.as_view("reset_req"),
        )
        self.email = "user@example.com"
        self.payload = {"email": self.email}
        self.token_data = {"token": "abc123", "time": "2025-01-01 12:00:00"}

    @patch("app.controllers.user_controllers.NotificationService.send_password_reset")
    @patch("app.controllers.user_controllers.UserService.store_reset_token")
    def test_request_reset_success(self, mock_store_token, mock_send_reset):
        mock_store_token.return_value = self.token_data

        response = self.client.post("/request-reset", json=self.payload)
        self.assertEqual(response.status_code, 201)
        body = response.get_json()
        self.assertEqual(body["data"], self.token_data)
        self.assertIn("msg", body)
        mock_store_token.assert_called_once_with(self.email)
        mock_send_reset.assert_called_once()

    def test_request_reset_validation_error(self):
        from marshmallow import ValidationError

        with patch.object(
            RequestUserPasswordResetController.request_reset_password_schema,
            "load",
            side_effect=ValidationError("bad"),
        ):
            response = self.client.post("/request-reset", json={})
            self.assertEqual(response.status_code, 400)
            self.assertIn("validation_error", response.get_json())

    @patch("app.controllers.user_controllers.UserService.store_reset_token")
    def test_request_reset_returns_no_token_data(self, mock_store_token):
        mock_store_token.return_value = None

        response = self.client.post("/request-reset", json=self.payload)
        self.assertEqual(response.status_code, 500)
        self.assertIn("error", response.get_json())

    @patch("app.controllers.user_controllers.UserService.store_reset_token")
    def test_request_reset_unexpected_error(self, mock_store_token):
        mock_store_token.side_effect = Exception("kaboom")

        response = self.client.post("/request-reset", json=self.payload)
        self.assertEqual(response.status_code, 500)
        self.assertIn("generic_error", response.get_json())


class TestResetUserPasswordController(unittest.TestCase):
    """Tests for the password-reset endpoint."""

    def setUp(self):
        self.app = Flask(__name__)
        self.client = self.app.test_client()
        self.app.add_url_rule(
            "/reset-password",
            view_func=ResetUserPasswordController.as_view("reset_pwd"),
        )
        self.token = "validtoken"
        self.password = "newpassword123"
        self.payload = {
            "password": self.password,
            "confirm_password": self.password,
        }
        self.endpoint = f"/reset-password?token={self.token}"

    def test_reset_password_no_token(self):
        """A request with no token in the query string ultimately fails.

        The controller's guard `len(token) < 1 or None` evaluates to falsy
        when token is `None`, so the request falls through to the try block
        where the dummy "None" string fails the reset-token signature check.
        The generic error handler then returns a 500 with `generic_error`.
        """
        with patch(
            "app.controllers.user_controllers.Helpers.verify_reset_token",
            side_effect=Exception("Token is invalid or tampered with"),
        ):
            response = self.client.post(
                "/reset-password",
                json=self.payload,
            )
        # The controller falls through into the try block; a tampered-token
        # exception is raised and translated into a generic 500 response.
        self.assertEqual(response.status_code, 500)
        self.assertIn("generic_error", response.get_json())

    @patch("app.controllers.user_controllers.UserService.change_password")
    @patch("app.controllers.user_controllers.Helpers.verify_reset_token")
    def test_reset_password_success(self, mock_verify, mock_change):
        mock_verify.return_value = "user@example.com"
        mock_change.return_value = True

        response = self.client.post(self.endpoint, json=self.payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["msg"], "Password changed successfully")
        mock_verify.assert_called_once_with(self.token, 3600)
        mock_change.assert_called_once_with("user@example.com", self.password)

    @patch("app.controllers.user_controllers.Helpers.verify_reset_token")
    def test_reset_password_invalid_token(self, mock_verify):
        mock_verify.return_value = None

        response = self.client.post(self.endpoint, json=self.payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())

    @patch("app.controllers.user_controllers.UserService.change_password")
    @patch("app.controllers.user_controllers.Helpers.verify_reset_token")
    def test_reset_password_change_fails(self, mock_verify, mock_change):
        mock_verify.return_value = "user@example.com"
        mock_change.return_value = False

        response = self.client.post(self.endpoint, json=self.payload)
        self.assertEqual(response.status_code, 500)
        self.assertIn("error", response.get_json())

    @patch("app.controllers.user_controllers.Helpers.verify_reset_token")
    def test_reset_password_unexpected_error(self, mock_verify):
        mock_verify.side_effect = Exception("kaboom")

        response = self.client.post(self.endpoint, json=self.payload)
        self.assertEqual(response.status_code, 500)
        self.assertIn("generic_error", response.get_json())


if __name__ == "__main__":
    unittest.main()
