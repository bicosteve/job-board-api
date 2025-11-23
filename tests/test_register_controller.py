import unittest
from unittest.mock import patch
from flask import Flask, json
from marshmallow import ValidationError

from app.controllers.user_controllers import RegisterUserController
from app.utils.exceptions import UserExistError


class TestRegisterController(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.client = self.app.test_client()

        # add the resource endpoint manually
        self.app.add_url_rule(
            '/register', view_func=RegisterUserController.as_view('register'))

        self.email = 'john.doe@example.com'
        self.password = 'secure1234'

        self.payload = {
            'email': self.email,
            'password': self.password,
            'confirm_password': 'secure1234'
        }

    def test_register_validation_error(self):
        '''Should return 400 if the schema validation fails'''
        target = 'app.controllers.user_controllers.UserService.register_user'
        payload = {
            'email': self.email,
            'password': self.password
        }
        with patch(target) as mock_register:
            mock_register.side_effect = ValidationError('validation error')
            response = self.client.post(
                '/register',
                data=json.dumps(payload),
                content_type='application/json'
            )

            # Assertion
            self.assertEqual(response.status_code, 400)
            data = json.loads(response.data)
            self.assertIn('error', data)

    def test_register_user_already_exists(self):
        '''Should return 400 if user already exists'''
        target = 'app.controllers.user_controllers.UserService.register_user'
        with patch(target) as mock_register:
            mock_register.side_effect = UserExistError('user already exists')
            response = self.client.post(
                '/register',
                data=json.dumps(self.payload),
                content_type='application/json'
            )

            self.assertEqual(response.status_code, 400)
            data = json.loads(response.data)
            self.assertIn('user_error', data)

    def test_register_user_success(self):
        '''Should return 201 when user is successfully registered'''
        with patch('app.controllers.user_controllers.UserService.register_user') as mock_register, \
                patch('app.controllers.user_controllers.UserService.store_verification_code') as mock_store, \
                patch('app.controllers.user_controllers.Helpers.generate_verification_code') as mock_code, \
                patch('app.controllers.user_controllers.Logger') as mock_log:

            mock_register.return_value = {'rows_affected': 1}
            mock_store.return_value = True
            mock_code.return_value = '123456'

            response = self.client.post(
                '/register',
                data=json.dumps(self.payload),
                content_type='application/json')

            self.assertEqual(response.status_code, 201)
            data = json.loads(response.data)
            self.assertIn('msg', data)
            self.assertEqual(data['msg'], 'user created')
            self.assertEqual(data['email'], self.payload['email'])
            self.assertEqual(data['verification_code'], '123456')
            mock_register.assert_called_once()
            mock_store.assert_called_once()
            mock_code.assert_called_once()
            mock_log.info.assert_any_call(
                f'Attempting to register user: {self.payload["email"]}')
