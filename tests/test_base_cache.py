import unittest
from unittest.mock import patch, MagicMock
import json

from app.repositories.base_cache import BaseCache


class TestUserCache(unittest.TestCase):
    '''
    This class is used to test helper methods in UserCache
    '''

    def setUp(self):
        self.email = "user@example.com"
        self.code = "123456"
        self.token_data = {"token": self.code,
                           "created_at": "2025-01-01 12:00:00"}

    @patch("app.repositories.base_cache.Cache.connect_redis")
    def test_store_verification_code_success(self, mock_connect_redis):
        client = MagicMock()
        client.setex.return_value = True
        mock_connect_redis.return_value = client

        result = BaseCache.store_verification_code(self.email, self.code)

        client.setex.assert_called_once_with(
            f"verify#{self.email}", 6 * 60 * 60, self.code)
        self.assertTrue(result)

    @patch("app.repositories.base_cache.Cache.connect_redis")
    def test_store_verification_code_failure(self, mock_connect_redis):
        client = MagicMock()
        client.setex.return_value = False
        mock_connect_redis.return_value = client

        result = BaseCache.store_verification_code(self.email, self.code)
        self.assertFalse(result)

    @patch("app.repositories.base_cache.Cache.connect_redis")
    def test_verify_code_success(self, mock_connect_redis):
        client = MagicMock()
        client.get.return_value = self.code.encode('utf-8')
        mock_connect_redis.return_value = client

        result = BaseCache.verify_code(self.email, self.code)

        client.get.assert_called_once_with(f'verify#{self.email}')
        client.delete.assert_called_once_with(f'verify#{self.email}')
        self.assertTrue(result)

    @patch("app.repositories.base_cache.Cache.connect_redis")
    def test_verify_code_missing(self, mock_connect_redis):
        client = MagicMock()
        client.get.return_value = None
        mock_connect_redis.return_value = client

        result = BaseCache.verify_code(self.email, self.code)

        self.assertFalse(result)
        client.delete.assert_not_called()

    @patch("app.repositories.base_cache.Cache.connect_redis")
    def test_verify_code_mismatch(self, mock_connect_redis):
        client = MagicMock()
        client.get.return_value = "654321".encode('utf-8')
        mock_connect_redis.return_value = client

        result = BaseCache.verify_code(self.email, self.code)

        self.assertFalse(result)
        client.delete.assert_not_called()

    @patch("app.repositories.base_cache.Cache.connect_redis")
    def test_hold_reset_token_success(self, mock_connect_redis):
        client = MagicMock()
        client.setex.return_value = True
        mock_connect_redis.return_value = client

        result = BaseCache.hold_reset_token(self.email, self.token_data)

        client.setex.assert_called_once_with(
            f'reset#{self.email}', 60 * 60, json.dumps(self.token_data)
        )

        self.assertTrue(result)

    # retrieve_reset_token()
    @patch("app.repositories.base_cache.Helpers.compare_token_time", return_value=False)
    @patch("app.repositories.base_cache.Cache.connect_redis")
    def test_retrieve_reset_token_success(self, mock_connect_redis, mock_compare_token_time):
        client = MagicMock()
        client.get.return_value = json.dumps(self.token_data).encode('utf-8')
        mock_connect_redis.return_value = client

        result = BaseCache.retrieve_reset_token(self.email, self.code)

        client.get.assert_called_once_with(f'reset#{self.email}')
        client.delete.assert_called_once_with(f'reset#{self.email}')
        self.assertEqual(result, self.code)

    @patch("app.repositories.base_cache.Helpers.compare_token_time", return_value=True)
    @patch("app.repositories.base_cache.Cache.connect_redis")
    def test_retrieve_reset_token_expired(self, mock_connect_redis, mock_compare_token_time):
        client = MagicMock()
        client.get.return_value = json.dumps(self.token_data).encode('utf-8')
        mock_connect_redis.return_value = client

        result = BaseCache.retrieve_reset_token(self.email, self.code)

        self.assertIsNone(result)
        client.delete.assert_not_called()

    @patch("app.repositories.base_cache.Cache.connect_redis")
    def test_retrieve_reset_token_not_found(self, mock_connect_redis):
        client = MagicMock()
        client.get.return_value = None
        mock_connect_redis.return_value = client

        result = BaseCache.retrieve_reset_token(self.email, self.code)

        self.assertIsNone(result)
        client.delete.assert_not_called()

    @patch("app.repositories.base_cache.Cache.connect_redis")
    def test_retrieve_reset_token_mismatch(self, mock_connect_redis):
        client = MagicMock()
        client.get.return_value = json.dumps(
            {"token": "333444", "created_at": "timestamp"})
        mock_connect_redis.return_value = client

        result = BaseCache.retrieve_reset_token(self.email, self.code)

        self.assertIsNone(result)
        client.delete.assert_not_called()


if __name__ == '__main__':
    unittest.main()
