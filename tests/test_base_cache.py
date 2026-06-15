import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from app.repositories.base_cache import BaseCache


class TestBaseCache(unittest.TestCase):
    def setUp(self):
        self.email = "test@example.com"
        self.code = "123456"
        self.token = "sometoken"

    # ---------- store_verification_code ----------
    def test_store_verification_code_success(self):
        with patch("app.repositories.base_cache.Cache.connect_redis") as mock_connect:
            mock_client = MagicMock()
            mock_client.setex.return_value = True
            mock_connect.return_value = mock_client

            result = BaseCache.store_verification_code(self.email, self.code)

            self.assertTrue(result)
            mock_client.setex.assert_called_once_with(
                f"verify#{self.email}", 6 * 60 * 60, self.code
            )

    def test_store_verification_code_failure_returns_false(self):
        with patch("app.repositories.base_cache.Cache.connect_redis") as mock_connect:
            mock_client = MagicMock()
            mock_client.setex.return_value = False
            mock_connect.return_value = mock_client

            result = BaseCache.store_verification_code(self.email, self.code)

            self.assertFalse(result)

    def test_store_verification_code_uses_correct_ttl(self):
        """The TTL must equal 6 * 60 * 60 = 21,600 seconds."""
        with patch("app.repositories.base_cache.Cache.connect_redis") as mock_connect:
            mock_client = MagicMock()
            mock_client.setex.return_value = True
            mock_connect.return_value = mock_client

            BaseCache.store_verification_code(self.email, self.code)

            call_args = mock_client.setex.call_args[0]
            self.assertEqual(call_args[1], 6 * 60 * 60)

    # ---------- verify_code ----------
    def test_verify_code_success(self):
        with patch("app.repositories.base_cache.Cache.connect_redis") as mock_connect:
            mock_client = MagicMock()
            mock_client.get.return_value = self.code
            mock_connect.return_value = mock_client

            result = BaseCache.verify_code(self.email, self.code)

            self.assertTrue(result)
            mock_client.delete.assert_called_once_with(f"verify#{self.email}")

    def test_verify_code_failure_when_no_code(self):
        with patch("app.repositories.base_cache.Cache.connect_redis") as mock_connect:
            mock_client = MagicMock()
            mock_client.get.return_value = None
            mock_connect.return_value = mock_client

            result = BaseCache.verify_code(self.email, self.code)

            self.assertFalse(result)
            mock_client.delete.assert_not_called()

    def test_verify_code_failure_when_code_doesnt_match(self):
        with patch("app.repositories.base_cache.Cache.connect_redis") as mock_connect:
            mock_client = MagicMock()
            mock_client.get.return_value = "123456"
            mock_connect.return_value = mock_client

            result = BaseCache.verify_code(self.email, "999999")

            self.assertFalse(result)
            mock_client.delete.assert_not_called()

    def test_verify_code_handles_bytes_value(self):
        with patch("app.repositories.base_cache.Cache.connect_redis") as mock_connect:
            mock_client = MagicMock()
            mock_client.get.return_value = self.code.encode("utf-8")
            mock_connect.return_value = mock_client

            result = BaseCache.verify_code(self.email, self.code)

            self.assertTrue(result)
            mock_client.delete.assert_called_once_with(f"verify#{self.email}")

    # ---------- hold_reset_token ----------
    def test_hold_reset_token_success(self):
        with patch("app.repositories.base_cache.Cache.connect_redis") as mock_connect:
            mock_client = MagicMock()
            mock_client.setex.return_value = True
            mock_connect.return_value = mock_client

            data = {"token": self.token, "time": "2025-01-01 12:00:00"}
            result = BaseCache.hold_reset_token(self.email, data)

            self.assertTrue(result)
            mock_client.setex.assert_called_once()

    def test_hold_reset_token_failure_returns_false(self):
        with patch("app.repositories.base_cache.Cache.connect_redis") as mock_connect:
            mock_client = MagicMock()
            mock_client.setex.return_value = False
            mock_connect.return_value = mock_client

            data = {"token": self.token, "time": "2025-01-01 12:00:00"}
            result = BaseCache.hold_reset_token(self.email, data)

            self.assertFalse(result)

    def test_hold_reset_token_uses_one_hour_ttl(self):
        with patch("app.repositories.base_cache.Cache.connect_redis") as mock_connect:
            mock_client = MagicMock()
            mock_client.setex.return_value = True
            mock_connect.return_value = mock_client

            data = {"token": self.token, "time": "2025-01-01 12:00:00"}
            BaseCache.hold_reset_token(self.email, data)

            call_args = mock_client.setex.call_args[0]
            self.assertEqual(call_args[1], 60 * 60)

    # ---------- retrieve_reset_token ----------
    def test_retrieve_reset_token_returns_token_when_fresh_and_matching(self):
        with patch(
            "app.repositories.base_cache.Cache.connect_redis"
        ) as mock_connect, patch(
            "app.repositories.base_cache.Helpers.compare_token_time",
            return_value=False,
        ):
            mock_client = MagicMock()
            fresh_time = (datetime.now() - timedelta(minutes=1)).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            payload = f'{{"token": "{self.token}", "time": "{fresh_time}"}}'
            mock_client.get.return_value = payload
            mock_connect.return_value = mock_client

            result = BaseCache.retrieve_reset_token(self.email, self.token)

            self.assertEqual(result, self.token)
            mock_client.delete.assert_called_once_with(f"reset#{self.email}")

    def test_retrieve_reset_token_returns_none_when_not_in_cache(self):
        with patch("app.repositories.base_cache.Cache.connect_redis") as mock_connect:
            mock_client = MagicMock()
            mock_client.get.return_value = None
            mock_connect.return_value = mock_client

            result = BaseCache.retrieve_reset_token(self.email, self.token)

            self.assertIsNone(result)
            mock_client.delete.assert_not_called()

    def test_retrieve_reset_token_returns_none_when_token_mismatch(self):
        with patch(
            "app.repositories.base_cache.Cache.connect_redis"
        ) as mock_connect, patch(
            "app.repositories.base_cache.Helpers.compare_token_time",
            return_value=False,
        ):
            mock_client = MagicMock()
            fresh_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            payload = f'{{"token": "stored", "time": "{fresh_time}"}}'
            mock_client.get.return_value = payload
            mock_connect.return_value = mock_client

            result = BaseCache.retrieve_reset_token(self.email, "different-token")

            self.assertIsNone(result)
            mock_client.delete.assert_not_called()

    def test_retrieve_reset_token_returns_none_when_expired(self):
        with patch(
            "app.repositories.base_cache.Cache.connect_redis"
        ) as mock_connect, patch(
            "app.repositories.base_cache.Helpers.compare_token_time",
            return_value=True,
        ):
            mock_client = MagicMock()
            payload = '{"token": "x", "time": "2020-01-01 00:00:00"}'
            mock_client.get.return_value = payload
            mock_connect.return_value = mock_client

            result = BaseCache.retrieve_reset_token(self.email, "x")

            self.assertIsNone(result)
            mock_client.delete.assert_not_called()

    def test_retrieve_reset_token_returns_none_for_invalid_json(self):
        with patch("app.repositories.base_cache.Cache.connect_redis") as mock_connect:
            mock_client = MagicMock()
            mock_client.get.return_value = "not-valid-json"
            mock_connect.return_value = mock_client

            result = BaseCache.retrieve_reset_token(self.email, "x")

            self.assertIsNone(result)

    def test_retrieve_reset_token_handles_bytes(self):
        with patch(
            "app.repositories.base_cache.Cache.connect_redis"
        ) as mock_connect, patch(
            "app.repositories.base_cache.Helpers.compare_token_time",
            return_value=False,
        ):
            mock_client = MagicMock()
            fresh_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            payload = f'{{"token": "{self.token}", "time": "{fresh_time}"}}'
            mock_client.get.return_value = payload.encode("utf-8")
            mock_connect.return_value = mock_client

            result = BaseCache.retrieve_reset_token(self.email, self.token)

            self.assertEqual(result, self.token)

    def test_retrieve_reset_token_returns_none_when_token_key_missing(self):
        with patch(
            "app.repositories.base_cache.Cache.connect_redis"
        ) as mock_connect, patch(
            "app.repositories.base_cache.Helpers.compare_token_time",
            return_value=False,
        ):
            mock_client = MagicMock()
            payload = '{"time": "2025-01-01 12:00:00"}'
            mock_client.get.return_value = payload
            mock_connect.return_value = mock_client

            result = BaseCache.retrieve_reset_token(self.email, "x")

            self.assertIsNone(result)

    # ---------- get_client ----------
    def test_get_client_returns_redis_client(self):
        with patch("app.repositories.base_cache.Cache.connect_redis") as mock_connect:
            mock_client = MagicMock()
            mock_connect.return_value = mock_client

            client = BaseCache.get_client()

            self.assertIs(client, mock_client)
            mock_connect.assert_called_once()


if __name__ == "__main__":
    unittest.main()
