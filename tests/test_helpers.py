import os
import time
import unittest
from datetime import datetime, timedelta
from unittest.mock import patch

from app.utils.helpers import Helpers


class TestHelpers(unittest.TestCase):

    def setUp(self):
        self.email = "test@gmail.com"
        self.salt = "password-reset-salt"

    # ---------- generate_verification_code ----------
    def test_generate_verification_code_returns_six_digits(self):
        code = Helpers.generate_verification_code()
        self.assertEqual(len(code), 6)
        self.assertTrue(code.isdigit())
        self.assertGreaterEqual(int(code), 100_000)
        self.assertLessEqual(int(code), 999_999)

    def test_generate_verification_code_can_produce_different_values(self):
        """Statistical check: 100 codes should produce at least 2 unique values."""
        codes = {Helpers.generate_verification_code() for _ in range(100)}
        self.assertGreater(len(codes), 1)

    # ---------- generate_reset_token ----------
    @patch.dict(os.environ, {"SECRET_KEY": "some-secret"})
    def test_generate_reset_token_returns_signed_token(self):
        token = Helpers.generate_reset_token(self.email)
        self.assertTrue(token)
        self.assertIn(".", token)

    @patch.dict(os.environ, {"SECRET_KEY": "some-secret"})
    def test_generate_reset_token_distinct_for_distinct_emails(self):
        token_a = Helpers.generate_reset_token("a@example.com")
        token_b = Helpers.generate_reset_token("b@example.com")
        self.assertNotEqual(token_a, token_b)

    def test_generate_reset_token_produces_deterministic_token_per_email(self):
        """Same email with same serializer secret produces the same token (until exp)."""
        with patch.dict(os.environ, {"SECRET_KEY": "some-secret"}):
            token_a = Helpers.generate_reset_token(self.email)
            token_b = Helpers.generate_reset_token(self.email)
        self.assertEqual(token_a, token_b)

    # ---------- verify_reset_token ----------
    @patch.dict(os.environ, {"SECRET_KEY": "some-secret"})
    def test_verify_reset_token_returns_original_email_if_valid(self):
        token = Helpers.generate_reset_token(self.email)
        email = Helpers.verify_reset_token(token, 3600)
        self.assertEqual(email, self.email)

    @patch.dict(os.environ, {"SECRET_KEY": "some-secret"})
    def test_verify_reset_token_raises_for_invalid_token(self):
        with self.assertRaises(Exception) as context:
            Helpers.verify_reset_token("invalid.token", 3600)
        self.assertIn("invalid", str(context.exception).lower())

    @patch.dict(os.environ, {"SECRET_KEY": "some-secret"})
    def test_verify_reset_token_raises_for_expired_token(self):
        token = Helpers.generate_reset_token(self.email)
        time.sleep(2)
        with self.assertRaises(Exception) as ctx:
            Helpers.verify_reset_token(token, 1)
        self.assertIn("expired", str(ctx.exception).lower())

    @patch.dict(os.environ, {"SECRET_KEY": "some-secret"})
    def test_verify_reset_token_raises_for_tampered_token(self):
        """Mutating the token body should raise a BadSignature error."""
        token = Helpers.generate_reset_token(self.email)
        tampered = token[:-2] + "ab"
        with self.assertRaises(Exception):
            Helpers.verify_reset_token(tampered, 3600)

    @patch.dict(os.environ, {"SECRET_KEY": "some-secret"})
    def test_verify_reset_token_accepts_string_max_age(self):
        """The method should coerce a string max_age to int."""
        token = Helpers.generate_reset_token(self.email)
        # max_age as string should be coerced to int internally
        email = Helpers.verify_reset_token(token, "3600")
        self.assertEqual(email, self.email)

    @patch.dict(os.environ, {"SECRET_KEY": "some-secret"})
    def test_verify_reset_token_none_max_age_skips_expiry(self):
        token = Helpers.generate_reset_token(self.email)
        email = Helpers.verify_reset_token(token, None)
        self.assertEqual(email, self.email)

    # ---------- compare_token_time ----------
    def test_token_older_than_5_minutes_returns_true(self):
        old_time = datetime.now() - timedelta(minutes=10)
        data = {"time": old_time.strftime("%Y-%m-%d %H:%M:%S")}

        result = Helpers.compare_token_time(data)
        self.assertTrue(result)

    @patch("app.utils.helpers.datetime")
    def test_token_newer_than_5_minutes_returns_false(self, mock_datetime):
        fixed_now = datetime(2025, 1, 1, 12, 0, 0)
        mock_datetime.now.return_value = fixed_now
        mock_datetime.strptime = datetime.strptime

        recent_time = fixed_now - timedelta(minutes=3)
        data = {"time": recent_time.strftime("%Y-%m-%d %H:%M:%S")}
        result = Helpers.compare_token_time(data)
        self.assertFalse(result)

    @patch("app.utils.helpers.datetime")
    def test_token_exactly_minutes_returns_false(self, mock_datetime):
        fixed_now = datetime(2025, 1, 1, 12, 0, 0)
        mock_datetime.now.return_value = fixed_now
        mock_datetime.strptime = datetime.strptime

        exact_time = fixed_now - timedelta(minutes=5)
        data = {"time": exact_time.strftime("%Y-%m-%d %H:%M:%S")}
        result = Helpers.compare_token_time(data)
        self.assertFalse(result)

    @patch("app.utils.helpers.datetime")
    def test_token_just_under_5_minutes_returns_false(self, mock_datetime):
        """Token that is 4m59s old is still within the window."""
        fixed_now = datetime(2025, 1, 1, 12, 0, 0)
        mock_datetime.now.return_value = fixed_now
        mock_datetime.strptime = datetime.strptime

        almost_old = fixed_now - timedelta(minutes=4, seconds=59)
        data = {"time": almost_old.strftime("%Y-%m-%d %H:%M:%S")}
        result = Helpers.compare_token_time(data)
        self.assertFalse(result)

    @patch("app.utils.helpers.datetime")
    def test_token_just_over_5_minutes_returns_true(self, mock_datetime):
        """Token that is 5m1s old has expired."""
        fixed_now = datetime(2025, 1, 1, 12, 0, 0)
        mock_datetime.now.return_value = fixed_now
        mock_datetime.strptime = datetime.strptime

        just_old = fixed_now - timedelta(minutes=5, seconds=1)
        data = {"time": just_old.strftime("%Y-%m-%d %H:%M:%S")}
        result = Helpers.compare_token_time(data)
        self.assertTrue(result)

    def test_compare_token_time_missing_key_raises_key_error(self):
        """Missing 'time' key in payload should raise KeyError."""
        with self.assertRaises(KeyError):
            Helpers.compare_token_time({})

    def test_compare_token_time_invalid_format_raises_value_error(self):
        """A non-parseable time string should raise ValueError."""
        with self.assertRaises(ValueError):
            Helpers.compare_token_time({"time": "not-a-date"})


if __name__ == "__main__":
    unittest.main()
