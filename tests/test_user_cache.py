import unittest
from unittest.mock import patch, MagicMock
import json

from app.repositories.user_cache import UserCache


class TestUserCache(unittest.TestCase):
    '''
    This class is used to test helper methods in UserCache
    '''

    @patch("app.repositories.user_cache.Cache.connect_redis")
    def test_store_verification_code(self, mock_connect):
        mock_client = MagicMock()
        mock_connect.return_value = mock_client
        mock_client.setext.return_value = True

        data = {
            "email": "test@example.com",
            "code": "123456"
        }

        result = UserCache.store_verification_code(data['email'], data['code'])

        mock_client.setex.assert_called_once_with(
            "verify#test@example.com", 6 * 60 * 60, "123456")
        self.assertTrue

    @patch("app.repositories.user_cache.Cache.connect_redis")
    def test_verify_code_success(self, mock_connect):
        mock_client = MagicMock()
        mock_connect.return_value = mock_client
        mock_client.get.return_value = "123456"

        # Patch delete to succeed
        mock_client.delete.return_value = 1

        result = UserCache.verify_code("test@example.com", "123456")

        mock_client.get.assert_called_once_with("verify#test@example.com")
        mock_client.delete.assert_called_once_with("verify#test@example.com")
        self.assertTrue

    @patch("app.repositories.user_cache.Cache.connect_redis")
    def test_verify_code_failure_wrong_code(self, mock_connect):
        mock_client = MagicMock()
        mock_connect.return_value = mock_client
        mock_client.get.return_value = "999999"

        result = UserCache.verify_code("test@example.com", "123456")

        self.assertFalse(result)

    @patch("app.repositories.user_cache.Cache.connect_redis")
    def test_hold_reset_token(self, mock_connect):
        mock_client = MagicMock()
        mock_connect.return_value = mock_client
        mock_client.setex.return_value = True

        data = {"token": "abcd", "timestamp": "2025-11-06T20:00:00"}
        result = UserCache.hold_reset_token("test@example.com", data)

        mock_client.setex.assert_called_once_with(
            "reset#test@example.com", 60 * 60, json.dumps(data)
        )

        self.assertTrue(result)

    @patch("app.repositories.user_cache.Cache.connect_redis")
    @patch("app.repositories.user_cache.Helpers.compare_token_time")
    def test_reset_token_expired(self, mock_compare, mock_connect):
        mock_client = MagicMock()
        mock_connect.return_value = mock_client
        mock_client.get.return_value = json.dumps(
            {"token": "abcd", "timestamp": "2025-11-06T20:00:00"})
        mock_compare.return_value = True  # expired

        result = UserCache.retrieve_reset_token("test@example.com", "abcd")

        self.assertIsNone(result)

    @patch("app.repositories.user_cache.Cache.connect_redis")
    def test_retrieve_wrong_reset_token(self, mock_connect):
        mock_client = MagicMock()
        mock_connect.return_value = mock_client
        mock_client.get.return_value = json.dumps(
            {"token": "abcd", "timestamp": "2025-11-07T20:00:00"})

        result = UserCache.retrieve_reset_token("test@example.com", "wrong")

        self.assertIsNone(result)

    @patch("app.repositories.user_cache.Cache.connect_redis")
    def test_reset_token_retrieve_no_reset_token_failed(self, mock_connect):
        mock_client = MagicMock()
        mock_connect.return_value = mock_client
        mock_client.get.return_value = None

        result = UserCache.retrieve_reset_token("test@example.com", "abcd")

        self.assertIsNone(result)
