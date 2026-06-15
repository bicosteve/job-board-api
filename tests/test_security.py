import datetime
import os
import unittest
from unittest.mock import patch

import jwt

from app.utils.security import Security


class TestSecurity(unittest.TestCase):

    def setUp(self):
        # Set environment variables
        os.environ["JWT_SECRET"] = "testsecret"
        os.environ["JWT_ALGORITHM"] = "HS256"
        os.environ["JWT_TOKEN_EXPIRY_HOURS"] = "1"

        self.password = "my_secret_password_1234"
        self.profile_id = 1001
        self.email = "user@example.com"

    # ------------ 1. PASSWORD HASHING --------------------#
    def test_hash_password_returns_string(self):
        hashed = Security.hash_password(self.password)
        self.assertIsInstance(hashed, str)
        self.assertNotEqual(hashed, self.password)
        start = hashed.startswith("$2b$")
        end = hashed.startswith("$2a$")
        self.assertTrue(start or end)

    def test_hash_password_different_for_same_input(self):
        """Bcrypt uses a fresh salt every call so two hashes differ."""
        a = Security.hash_password(self.password)
        b = Security.hash_password(self.password)
        self.assertNotEqual(a, b)

    def test_check_password_correct(self):
        hashed = Security.hash_password(self.password)
        result = Security.check_password(self.password, hashed)
        self.assertTrue(result)

    def test_check_password_wrong(self):
        hashed = Security.hash_password(self.password)
        result = Security.check_password("not-the-password", hashed)
        self.assertFalse(result)

    def test_check_password_empty(self):
        hashed = Security.hash_password(self.password)
        self.assertFalse(Security.check_password("", hashed))

    # ------------- 2. JWT TOKEN CREATION ----------------#
    def test_create_jwt_token_returns_string(self):
        token = Security.create_jwt_token(self.profile_id, self.email)
        self.assertIsInstance(token, str)
        self.assertTrue(len(token) > 0)

    def test_create_jwt_token_contains_profile_and_email(self):
        token = Security.create_jwt_token(self.profile_id, self.email)
        algorithm = os.getenv("JWT_ALGORITHM")
        decoded = jwt.decode(
            token, str(os.getenv("JWT_SECRET")), algorithms=[str(algorithm)]
        )

        self.assertEqual(decoded["profile_id"], self.profile_id)
        self.assertEqual(decoded["email"], self.email)
        self.assertIn("iat", decoded)
        self.assertIn("exp", decoded)

    def test_create_jwt_token_uses_default_expiry(self):
        """When JWT_TOKEN_EXPIRY_HOURS is unset, default 24h is used."""
        env = {k: v for k, v in os.environ.items() if k != "JWT_TOKEN_EXPIRY_HOURS"}
        with patch.dict(os.environ, env, clear=True):
            token = Security.create_jwt_token(self.profile_id, self.email)
        decoded = Security.decode_jwt_token(token)
        # exp and iat are Unix timestamps (ints) so the difference is seconds.
        delta_seconds = decoded["exp"] - decoded["iat"]
        self.assertAlmostEqual(delta_seconds, 24 * 3600, delta=60)

    def test_create_jwt_token_raises_when_secret_missing(self):
        env = {k: v for k, v in os.environ.items() if k != "JWT_SECRET"}
        with patch.dict(os.environ, env, clear=True):
            with self.assertRaises(ValueError) as ctx:
                Security.create_jwt_token(self.profile_id, self.email)
        self.assertIn("JWT_Secret", str(ctx.exception))

    def test_create_jwt_token_raises_when_algorithm_missing(self):
        env = {k: v for k, v in os.environ.items() if k != "JWT_ALGORITHM"}
        with patch.dict(os.environ, env, clear=True):
            with self.assertRaises(ValueError) as ctx:
                Security.create_jwt_token(self.profile_id, self.email)
        self.assertIn("JWT_ALGORITHM", str(ctx.exception))

    # ---------- 3. JWT DECODING ------------------------#
    def test_decode_jwt_valid_token(self):
        token = Security.create_jwt_token(self.profile_id, self.email)
        payload = Security.decode_jwt_token(token)
        self.assertEqual(payload["profile_id"], self.profile_id)
        self.assertEqual(payload["email"], self.email)

    def test_decode_jwt_token_invalid(self):
        fake_token = "invalid.token.here"
        with self.assertRaises(Exception) as context:
            Security.decode_jwt_token(fake_token)
        self.assertIn("Invalid token", str(context.exception))

    def test_decode_jwt_token_empty(self):
        with self.assertRaises(Exception) as context:
            Security.decode_jwt_token("")
        self.assertIn("Invalid token", str(context.exception))

    def test_decode_jwt_expired_token(self):
        time_one = datetime.datetime.now(datetime.timezone.utc)
        time_two = datetime.timedelta(seconds=1)
        iat_time = datetime.datetime.now(datetime.timezone.utc)
        expired_payload = {
            "profile_id": self.profile_id,
            "email": self.email,
            "exp": int((time_one - time_two).timestamp()),
            "iat": int(iat_time.timestamp()),
        }

        token = jwt.encode(
            expired_payload,
            str(os.getenv("JWT_SECRET")),
            algorithm=os.getenv("JWT_ALGORITHM"),
        )

        with self.assertRaises(Exception) as context:
            Security.decode_jwt_token(token)
        self.assertIn("Token expired", str(context.exception))

    def test_decode_jwt_raises_when_secret_missing(self):
        token = Security.create_jwt_token(self.profile_id, self.email)
        env = {k: v for k, v in os.environ.items() if k != "JWT_SECRET"}
        with patch.dict(os.environ, env, clear=True):
            with self.assertRaises(ValueError) as ctx:
                Security.decode_jwt_token(token)
        self.assertIn("JWT_Secret", str(ctx.exception))

    def test_decode_jwt_raises_when_algorithm_missing(self):
        token = Security.create_jwt_token(self.profile_id, self.email)
        env = {k: v for k, v in os.environ.items() if k != "JWT_ALGORITHM"}
        with patch.dict(os.environ, env, clear=True):
            with self.assertRaises(ValueError) as ctx:
                Security.decode_jwt_token(token)
        self.assertIn("JWT_ALGORITHM", str(ctx.exception))

    def test_decode_jwt_wrong_secret_raises_invalid(self):
        """Token signed with a different secret fails decoding."""
        token = jwt.encode(
            {"profile_id": 1, "email": "x", "exp": 9999999999},
            "different-secret",
            algorithm="HS256",
        )
        with self.assertRaises(Exception) as ctx:
            Security.decode_jwt_token(token)
        self.assertIn("Invalid token", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
