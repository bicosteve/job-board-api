import unittest
import os
import time
from datetime import datetime, timedelta
from unittest.mock import patch


from app.utils.helpers import Helpers


class TestHelpers(unittest.TestCase):

    def setUp(self):
        self.email = 'test@gmail.com'
        self.salt = 'password-reset-salt'

    def test_generate_verification_code_returns_six_digits(self):
        code = Helpers.generate_verification_code()
        self.assertEqual(len(code), 6)
        self.assertTrue(code.isdigit())

    @patch.dict(os.environ, {'SECRET_KEY': 'some-secret'})
    def test_generate_reset_token_returns_signed_token(self):
        token = Helpers.generate_reset_token(self.email)
        self.assertTrue(token)
        self.assertIn('.', token)

    @patch.dict(os.environ, {'SECRET_KEY': 'some-secret'})
    def test_verify_reset_token_returns_original_email_if_valid(self):
        token = Helpers.generate_reset_token(self.email)
        email = Helpers.verify_reset_token(token, 3600)
        self.assertEqual(email, self.email)

    @patch.dict(os.environ, {'SECRET_KEY': 'some-secret'})
    def test_verify_reset_token_raises_for_invalid_token(self):
        with self.assertRaises(Exception) as context:
            Helpers.verify_reset_token('invalid.token', 3600)
        self.assertIn('invalid', str(context.exception).lower())

    @patch.dict(os.environ, {'SECRET_KEY': 'some-secret'})
    def test_verify_reset_token_raises_for_expired_token(self):
        token = Helpers.generate_reset_token(self.email)
        time.sleep(2)
        with self.assertRaises(Exception):
            Helpers.verify_reset_token(token, 1)

    def test_token_older_than_5_minutes_returns_true(self):
        old_time = datetime.now() - timedelta(minutes=10)
        data = {'time': old_time.strftime('%Y-%m-%d %H:%M:%S')}

        result = Helpers.compare_token_time(data)
        self.assertTrue(result)

    @patch('app.utils.helpers.datetime')
    def test_token_newer_than_5_minutes_returns_false(self, mock_datetime):
        fixed_now = datetime(2025, 1, 1, 12, 0, 0)
        mock_datetime.now.return_value = fixed_now
        mock_datetime.strptime = datetime.strptime

        recent_time = fixed_now - timedelta(minutes=3)
        data = {'time': recent_time.strftime('%Y-%m-%d %H:%M:%S')}
        result = Helpers.compare_token_time(data)
        self.assertFalse(result)

    @patch('app.utils.helpers.datetime')
    def test_token_exactly_minutes_returns_false(self, mock_datetime):
        fixed_now = datetime(2025, 1, 1, 12, 0, 0)
        mock_datetime.now.return_value = fixed_now
        mock_datetime.strptime = datetime.strptime

        exact_time = fixed_now - timedelta(minutes=5)
        data = {'time': exact_time.strftime('%Y-%m-%d %H:%M:%S')}
        result = Helpers.compare_token_time(data)
        self.assertFalse(result)
