import unittest
import os
import jwt
import datetime

from app.utils.security import Security


class TestSecurity(unittest.TestCase):

    def setUp(self):
        # Set environment variables
        os.environ['JWT_SECRET'] = 'testsecret'
        os.environ['JWT_ALGORITHM'] = 'HS256'
        os.environ['JWT_TOKEN_EXPIRY_HOURS'] = '1'

        self.password = 'my_secret_password_1234'
        self.profile_id = 1001
        self.email = 'user@example.com'

    # ------------ 1. PASSWORD HASHING --------------------#
    def test_hash_password_returns_string(self):
        hashed = Security.hash_password(self.password)
        self.assertIsInstance(hashed, str)
        self.assertNotEqual(hashed, self.password)
        start = hashed.startswith('$2b$')
        end = hashed.startswith('$2a$')
        self.assertTrue(start or end)

    def test_check_password_correct(self):
        hashed = Security.hash_password(self.password)
        result = Security.check_password(self.password, hashed)
        self.assertTrue(result)

    # ------------- 2. JWT TOKEN CREATION ----------------#
    def test_create_jwt_token_returns_string(self):
        token = Security.create_jwt_token(self.profile_id, self.email)
        self.assertIsInstance(token, str)

    def test_create_jwt_token_contains_profile_and_email(self):
        token = Security.create_jwt_token(self.profile_id, self.email)
        algorithm = os.getenv('JWT_ALGORITHM')
        decoded = jwt.decode(token, str(os.getenv(
            'JWT_SECRET')), algorithms=[str(algorithm)])

        self.assertEqual(decoded['profile_id'], self.profile_id)
        self.assertEqual(decoded['email'], self.email)

    # ---------- 3. JWT DECODING ------------------------#
    def test_decode_jwt_valid_token(self):
        token = Security.create_jwt_token(self.profile_id, self.email)
        payload = Security.decode_jwt_token(token)
        self.assertEqual(payload['profile_id'], self.profile_id)
        self.assertEqual(payload['email'], self.email)

    def test_decode_jwt_token_invalid(self):
        fake_token = 'invalid.token.here'
        with self.assertRaises(Exception) as context:
            Security.decode_jwt_token(fake_token)
        self.assertIn('Invalid token', str(context.exception))

    def test_decode_jwt_expired_token(self):
        time_one = datetime.datetime.now(datetime.timezone.utc)
        time_two = datetime.timedelta(seconds=1)
        iat_time = datetime.datetime.now(datetime.timezone.utc)
        expired_payload = {
            'profile_id': self.profile_id,
            'email': self.email,
            'exp': int((time_one - time_two).timestamp()),
            'iat': int(iat_time.timestamp())
        }

        token = jwt.encode(
            expired_payload,
            str(os.getenv('JWT_SECRET')),
            algorithm=os.getenv('JWT_ALGORITHM'),
        )

        with self.assertRaises(Exception) as context:
            Security.decode_jwt_token(token)
        self.assertIn('Token expired', str(context.exception))


if __name__ == '__main__':
    unittest.main()
