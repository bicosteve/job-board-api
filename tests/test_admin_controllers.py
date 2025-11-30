import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
from flask_restful import Api
from marshmallow import ValidationError

from app.controllers.admin_controllers import (
    RegisterAdminController,
    LoginAdminController,
    VerifyAdminAccountController,
)
from app.utils.exceptions import (
    UserExistError,
    InvalidCredentialsError
)


class TestAdminControllers(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        api = Api(self.app)
        api.add_resource(RegisterAdminController, "/register")
        api.add_resource(LoginAdminController, "/login")
        api.add_resource(VerifyAdminAccountController, "/verify")
        self.client = self.app.test_client()

        self.email = "admin@example.com"
        self.password = "secret"
        self.payload = {"email": self.email, "password": self.password}

    # --- RegisterAdminController ---
    @patch("app.controllers.admin_controllers.RegisterAdminSchema.load")
    @patch("app.controllers.admin_controllers.Helpers.generate_verification_code", return_value="123456")
    @patch("app.controllers.admin_controllers.AdminService.add_admin_user")
    def test_register_admin_success(self, mock_add_admin, mock_code, mock_load):
        mock_load.return_value = {"email": self.email, "username": "admin"}
        mock_add_admin.return_value = {"rows": 1}

        res = self.client.post(
            "/register", json={"email": self.email, "username": "admin"})
        self.assertEqual(res.status_code, 201)
        self.assertIn("msg", res.get_json())
        self.assertEqual(res.get_json()["msg"], "Admin created")

    @patch("app.controllers.admin_controllers.RegisterAdminSchema.load", side_effect=ValidationError("bad payload"))
    def test_register_admin_validation_error(self, mock_load):
        res = self.client.post("/register", json={"email": self.email})
        self.assertEqual(res.status_code, 400)

    @patch("app.controllers.admin_controllers.RegisterAdminSchema.load")
    @patch("app.controllers.admin_controllers.AdminService.add_admin_user", return_value=None)
    def test_register_admin_service_none(self, mock_add_admin, mock_load):
        mock_load.return_value = {"email": self.email}
        res = self.client.post("/register", json={"email": self.email})
        self.assertEqual(res.status_code, 500)
        self.assertIn("msg", res.get_json())

    @patch("app.controllers.admin_controllers.RegisterAdminSchema.load")
    @patch("app.controllers.admin_controllers.AdminService.add_admin_user", side_effect=UserExistError("exists"))
    def test_register_admin_user_exists(self, mock_add_admin, mock_load):
        mock_load.return_value = {"email": self.email}
        res = self.client.post("/register", json={"email": self.email})
        self.assertEqual(res.status_code, 409)

    # --- LoginAdminController ---
    @patch("app.controllers.admin_controllers.LoginAdminSchema.load")
    @patch("app.controllers.admin_controllers.AdminService.get_admin_user")
    def test_login_admin_success(self, mock_get_admin, mock_load):
        mock_load.return_value = {
            "email": self.email, "password": self.password}
        mock_get_admin.return_value = {
            "id": 1, "email": self.email, "token": "jwt-token"}
        res = self.client.post("/login", json=self.payload)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["token"], "jwt-token")

    @patch("app.controllers.admin_controllers.LoginAdminSchema.load")
    @patch("app.controllers.admin_controllers.AdminService.get_admin_user", return_value=None)
    def test_login_admin_service_none(self, mock_get_admin, mock_load):
        mock_load.return_value = {
            "email": self.email, "password": self.password}
        res = self.client.post("/login", json=self.payload)
        self.assertEqual(res.status_code, 500)
        self.assertIn("error", res.get_json())

    @patch("app.controllers.admin_controllers.LoginAdminSchema.load", side_effect=ValidationError("bad payload"))
    def test_login_admin_validation_error(self, mock_load):
        res = self.client.post("/login", json=self.payload)
        self.assertEqual(res.status_code, 400)

    @patch("app.controllers.admin_controllers.LoginAdminSchema.load")
    @patch("app.controllers.admin_controllers.AdminService.get_admin_user", side_effect=InvalidCredentialsError("bad creds"))
    def test_login_admin_invalid_credentials(self, mock_get_admin, mock_load):
        mock_load.return_value = {
            "email": self.email, "password": self.password}
        res = self.client.post("/login", json=self.payload)
        self.assertEqual(res.status_code, 401)

    # --- VerifyAdminAccountController ---
    @patch("app.controllers.admin_controllers.VerifyAdminSchema.load")
    @patch("app.controllers.admin_controllers.AdminService.verify_admin_user")
    def test_verify_admin_success(self, mock_verify, mock_load):
        mock_load.return_value = {
            "email": self.email, "verification_code": "123456"}
        mock_verify.return_value = {"rows": 1}
        res = self.client.post(
            "/verify", json={"email": self.email, "verification_code": "123456"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["msg"], "account verified")

    @patch("app.controllers.admin_controllers.VerifyAdminSchema.load")
    @patch("app.controllers.admin_controllers.AdminService.verify_admin_user", return_value=None)
    def test_verify_admin_service_none(self, mock_verify, mock_load):
        mock_load.return_value = {
            "email": self.email, "verification_code": "123456"}
        res = self.client.post(
            "/verify", json={"email": self.email, "verification_code": "123456"})
        self.assertEqual(res.status_code, 500)

    @patch("app.controllers.admin_controllers.VerifyAdminSchema.load", side_effect=ValidationError("bad payload"))
    def test_verify_admin_validation_error(self, mock_load):
        res = self.client.post(
            "/verify", json={"email": self.email, "verification_code": "123456"})
        self.assertEqual(res.status_code, 400)
