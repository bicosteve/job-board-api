from datetime import datetime, timedelta

from ..repositories.user_repository import UserRepository
from ..repositories.user_cache import UserCache
from ..utils.security import Security
from ..utils.exceptions import (
    InvalidCredentialsError,
    UserExistError,
    GenericDatabaseError,
    InvalidLoginAttemptError,
    InvalidPasswordResetError,
    GenericRedisError,
    GenericGenerateResetTokenError,
    GenericPasswordHashError,
)
from ..utils.helpers import Helpers
from ..utils.logger import Loggger


class UserService:
    @staticmethod
    def get_user_profile(user_id):
        user_profile = UserRepository.find_user_by_id(user_id)
        if not user_profile:
            raise GenericDatabaseError("error occured while finding user")
        user = {
            "profile_id": user_profile.get("profile_id"),
            "email": user_profile.get("email"),
            "photo": user_profile.get("photo"),
            "status": user_profile.get("status"),
            "reset_token": user_profile.get("reset_token"),
            "created_at": user_profile.get("created_at"),
            "modified_at": user_profile.get("modified_at"),
        }
        return user

    @staticmethod
    def get_user(email, password):
        user = UserRepository.find_user_by_mail(email)
        if not user:
            Loggger.warn(f'user not found for email {email}')
            raise InvalidCredentialsError("Invalid email")
        if user["status"] != 1:
            Loggger.warn(f'user not verified for {email}')
            raise InvalidLoginAttemptError("Your account is not verified")
        if not Security.check_password(password, user["hash"]):
            Loggger.warn(f'Invalid password for user {email}')
            raise InvalidCredentialsError("Invalid email or password")
        return user

    @staticmethod
    def register_user(username, email, password):
        exists = UserRepository.find_user_by_mail(email)
        if exists:
            Loggger.warn(f'user does not exist for email {email}')
            raise UserExistError("user already exists")
        hash = Security.hash_password(password)
        status = 0
        result = UserRepository.add_user(email, hash, status)
        if result < 1:
            Loggger.error(f'error adding user to db')
            raise GenericDatabaseError("error occured while adding user")
        return {"rows_affected": result}

    @staticmethod
    def store_verification_code(email, code) -> bool:
        return UserCache.store_verification_code(email, code)

    @staticmethod
    def verify_account(email, code) -> bool:
        try:
            if UserCache.verify_code(email, code):
                return True
            return UserRepository.update_user_status(email) > 0
        except Exception as e:
            Loggger.exception(str(e))
            raise GenericDatabaseError(str(e))

    @staticmethod
    def store_reset_token(email: str) -> dict:
        try:
            token = Helpers.generate_reset_token(email)
            if not token:
                raise GenericGenerateResetTokenError(
                    'An error occured while generating reset token')
            data = {
                'token' : token,
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            isHeld = UserCache.hold_reset_token(email, data)
            if not isHeld:
                Loggger.error(
                    'An error occurred while storing reset token in redis')
                raise GenericRedisError(
                    'An error occurred while storing reset token in redis')
            if not UserRepository.store_reset_token(token) > 0:
                Loggger.error(
                    'An error occured while storing reset token')
                raise GenericDatabaseError(
                    'An error occured while storing reset token')
            return data
        except Exception as e:
            Loggger.exception(str(e))
            raise GenericDatabaseError(str(e))

    @staticmethod
    def get_reset_token(email: str, submitted_token: str) -> str:
        try:
            tkn = UserCache.retrieve_reset_token(email, submitted_token)
            if not tkn:
                data = UserRepository.get_reset_token(email)
                if not data:
                    Loggger.error(f'no token found for {email}')
                    raise InvalidPasswordResetError(
                        "No reset token found")
                if data['reset-token'] != submitted_token:
                    Loggger.error(f'Reset token do not match for {email}')
                    raise InvalidPasswordResetError(
                        "Wrong password reset token")
                if not Helpers.compare_token_time(data):
                    Loggger.warn("The reset token has expired")
                    raise InvalidPasswordResetError(
                        "The reset token has expired")
                return data['reset-token']
            return tkn
        except Exception as e:
            Loggger.exception(str(e))
            raise GenericDatabaseError(str(e))

    @staticmethod
    def change_password(email: str, password: str) -> bool:
        try:
            hashed_password = Security.hash_password(password)
        except Exception as e:
            Loggger.exception(str(e))
            raise GenericPasswordHashError(
                'There is a problem generating password hash')

        try:
            return UserRepository.update_password(email, hashed_password) > 0
        except Exception as e:
            Loggger.exception(str(e))
            raise GenericDatabaseError(str(e))
