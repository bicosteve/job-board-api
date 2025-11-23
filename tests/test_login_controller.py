import unittest
from unittest.mock import patch
from flask import Flask
from marshmallow import ValidationError

from app.controllers.user_controllers import LoginUserController
from app.utils.exceptions import InvalidCredentialsError


class TestLoginController(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.client = self.app.test_client()
        self.endpoint = '/login'
        self.email = 'john.doe@gamil.com'
        self.password = 'pass123'

        self.app.add_url_rule(
            self.endpoint, view_func=LoginUserController.as_view('login')
        )

        self.payload = {
            'email': self.email,
            'password': self.password
        }

    def test_login_validate_empty_payload(self):
        'Should return 400 if the schema is not valid'
        t = 'app.controllers.user_controllers.LoginUserController.login_schema.load'
        with patch(t) as mock_load:
            mock_load.side_effect = ValidationError('error')
            response = self.client.post(self.endpoint, json={})
            self.assertEqual(response.status_code, 400)
            self.assertIn('error', response.get_json())

    def test_login_validate_missing_email(self):
        'Should return 400 if the schema is not valid'
        t = 'app.controllers.user_controllers.LoginUserController.login_schema.load'
        with patch(t) as mock_load:
            mock_load.side_effect = ValidationError('error')
            response = self.client.post(
                self.endpoint, json={'password': self.password})
            self.assertEqual(response.status_code, 400)
            self.assertIn('error', response.get_json())

    def test_login_validate_missing_password(self):
        'Should return 400 if the schema is not valid'
        t = 'app.controllers.user_controllers.LoginUserController.login_schema.load'
        with patch(t) as mock_load:
            mock_load.side_effect = ValidationError('error')
            response = self.client.post(
                self.endpoint, json={'email': self.email})
            self.assertEqual(response.status_code, 400)
            self.assertIn('error', response.get_json())

    @patch('app.controllers.user_controllers.UserService.get_user')
    @patch('app.controllers.user_controllers.LoginUserController.login_schema.load')
    def test_login_user_not_found(self, mock_load, mock_get_user):
        'Should return 404 if user not found'
        mock_load.return_value = self.payload
        mock_get_user.return_value = None

        response = self.client.post(
            self.endpoint, json=self.payload)

        self.assertEqual(response.status_code, 404)
        self.assertIn('msg', response.get_json())

    @patch('app.controllers.user_controllers.Security.create_jwt_token')
    @patch('app.controllers.user_controllers.UserService.get_user')
    @patch('app.controllers.user_controllers.LoginUserController.login_schema.load')
    def test_login_user_not_found_500(self, mock_load, mock_get_user, mock_token):
        'Should return 500 if token generation fails'
        mock_load.return_value = self.payload
        mock_get_user.return_value = {'user_id': 1, 'email': self.email}
        mock_token.return_value = None

        response = self.client.post(
            self.endpoint, json=self.payload)

        self.assertEqual(response.status_code, 500)
        self.assertIn('msg', response.get_json())
        self.assertEqual(response.get_json()['msg'], 'Token generation failed')

    @patch('app.controllers.user_controllers.Security.create_jwt_token')
    @patch('app.controllers.user_controllers.UserService.get_user')
    @patch('app.controllers.user_controllers.LoginUserController.login_schema.load')
    def test_login_user_found(self, mock_load, mock_get_user, mock_token):
        'Should return 200 JWT token if login succeeds'
        mock_load.return_value = self.payload
        mock_get_user.return_value = {'user_id': 1,
                                      'email': self.email,
                                      'token': 'jwt-token-123'
                                      }
        mock_token.return_value = 'jwt-token-123'

        response = self.client.post(
            self.endpoint, json=self.payload)

        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['msg'], 'Login success')
        self.assertEqual(response.get_json()['token'], 'jwt-token-123')
        self.assertIn('Authorization', response.headers)

    @patch('app.controllers.user_controllers.UserService.get_user')
    @patch('app.controllers.user_controllers.LoginUserController.login_schema.load')
    def test_login_user_invalid_credentials(self, mock_load, mock_get_user):
        'Should return 401 for InvalidCredentialsError is raised'
        mock_load.return_value = self.payload
        mock_get_user.side_effect = InvalidCredentialsError('Wrong password')

        response = self.client.post(
            self.endpoint, json=self.payload)

        self.assertEqual(response.status_code, 401)
        self.assertIn('credentials_error', response.get_json())

    @patch("app.controllers.user_controllers.Security.create_jwt_token")
    @patch("app.controllers.user_controllers.UserService.get_user")
    @patch("app.controllers.user_controllers.LoginUserController.login_schema.load")
    def test_token_generation_err(self, mock_load, mock_get_user, mock_token):
        '''Should return 500 when token generation fails'''
        mock_load.return_value = {
            "email": self.email, "password": self.password}
        mock_get_user.return_value = {"user_id": 1, "email": self.email}
        mock_token.return_value = None

        res = self.client.post(self.endpoint, json=self.payload)

        self.assertEqual(res.status_code, 500)
        self.assertIn("msg", res.get_json())
        self.assertEqual(res.get_json()['msg'], "Token generation failed")

    @patch("app.controllers.user_controllers.UserService.get_user")
    @patch("app.controllers.user_controllers.LoginUserController.login_schema.load")
    def test_login_unexpected_error(self, mock_load, mock_get_user):
        '''Should return 500 if an unexpected exception occurs'''
        mock_load.return_value = {
            'email': self.email, 'password': self.password}
        mock_get_user.side_effect = Exception("Unexpected error")

        res = self.client.post(self.endpoint, json=self.payload)

        self.assertEqual(res.status_code, 500)
        self.assertIn("generic_error", res.get_json())
