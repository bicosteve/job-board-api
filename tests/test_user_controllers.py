import unittest
from unittest.mock import patch
from flask import Flask, json

from app.controllers.user_controllers import UserRegister
from app.utils.exceptions import UserExistError, GenericDatabaseError


class TestRegisterController(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.client = self.app.test_client()

        # add the resource endpoint manually
        self.app.add_url_rule(
            '/register', view_func=UserRegister.as_view('register'))

        self.payload = {
            'email': 'john.doe@example.com',
            'password': 'secure1234',
            'confirm_password': 'secure1234'
        }

    def test_register_user_success(self):
        '''Should return 201 when user is successfully registered'''

        with patch('app.controllers.user_controllers.UserService.register_user') as mock_register, \
                patch('app.controllers.user_controllers.UserService.store_verification_code') as mock_store, \
                patch('app.controllers.user_controllers.Helpers.generate_verification_code') as mock_code, \
                patch('app.controllers.user_controllers.Loggger') as mock_log:

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
