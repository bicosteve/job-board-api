import os
import random
from datetime import datetime, timedelta


from itsdangerous import (
    URLSafeTimedSerializer,
    SignatureExpired,
    BadSignature,
)


secret_key = os.getenv("SECRET_KEY", "dev_secret_key")
expiry_time = os.getenv("RESET_TIME", 3600)
s = URLSafeTimedSerializer(secret_key)


class Helpers:
    @staticmethod
    def generate_verification_code():
        return str(random.randint(100_000, 999_999))

    @staticmethod
    def generate_reset_token(email) -> str:
        return s.dumps(email, salt="password-reset-salt")

    @staticmethod
    def verify_reset_token(token, max_age=expiry_time) -> str | None:
        if max_age is not None and isinstance(max_age, str):
            max_age = int(max_age)
        try:
            email = s.loads(token, salt="password-reset-salt", max_age=max_age)
            return email
        except SignatureExpired:
            raise Exception("Signature expired")
        except BadSignature:
            raise Exception("Token is invalid or tampered with")

    @staticmethod
    def compare_token_time(data: dict) -> bool:
        time_in_string = data["time"]
        time_format = "%Y-%m-%d %H:%M:%S"
        stored_time = datetime.strptime(time_in_string, time_format)
        now = datetime.now()
        time_difference = now - stored_time
        return time_difference > timedelta(minutes=5)
