import os
import datetime
import bcrypt
import jwt
from dotenv import load_dotenv

load_dotenv()


class Security:

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash plain text password using bcrypt.
        Returns the hashed password as a UTF-8 string.
        """
        salt = bcrypt.gensalt()
        hash = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hash.decode("utf-8")

    @staticmethod
    def check_password(password: str, password_hash: str) -> bool:
        """
        Verifies the plain password against the hashed password.
        """
        return bcrypt.checkpw(
            password.encode("utf-8"),
            password_hash.encode("utf-8"),
        )

    @staticmethod
    def create_jwt_token(profile_id, email) -> str:
        """Generate jwt token with profile_id and email as payload"""
        secret = os.getenv('JWT_SECRET')
        algorithm = os.getenv('JWT_ALGORITHM')
        expiry_hours = int(os.getenv('JWT_TOKEN_EXPIRY_HOURS', '24'))
        now = datetime.datetime.now(datetime.UTC)
        exp_time = now + datetime.timedelta(hours=expiry_hours)

        payload = {
            "profile_id": profile_id,
            "email": email,
            "exp": exp_time,
            "iat": now,
        }

        token = jwt.encode(payload, secret, algorithm=algorithm)

        return token

    @staticmethod
    def decode_jwt_token(token):
        """Decodes jwt token and returns profile object"""
        secret = os.getenv('JWT_SECRET')
        algorithm = os.getenv('JWT_ALGORITHM')

        try:
            payload = jwt.decode(token, secret, algorithms=[algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise Exception("Token expired")
        except jwt.InvalidTokenError:
            raise Exception("Invalid token")
