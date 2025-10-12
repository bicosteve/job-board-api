import os
import datetime
import bcrypt
import jwt
from dotenv import load_dotenv

load_dotenv()


class Security:
    _algorithm = os.getenv("JWT_ALGORITHM")
    _now = datetime.datetime.now(datetime.UTC)
    _secret = os.getenv("JWT_SECRET")

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

        exp_time = Security._now + datetime.timedelta(hours=24 * 1)
        payload = {
            "profile_id": profile_id,
            "email": email,
            "exp": exp_time,
            "iat": Security._now,
        }

        token = jwt.encode(payload, Security._secret, algorithm=Security._algorithm)

        return token

    @staticmethod
    def decode_jwt_token(token):
        """Decodes jwt token and returns profile object"""
        try:
            payload = jwt.decode(token, Security._secret, Security._algorithm)
            return payload
        except jwt.ExpiredSignatureError:
            raise Exception("Token expired")
        except jwt.InvalidTokenError:
            raise Exception("Invalid token")
