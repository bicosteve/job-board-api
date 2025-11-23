from datetime import datetime

from ..repositories.user_repository import UserRepository
from ..repositories.base_cache import BaseCache
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
    UserDoesNotExistError
)
from ..utils.helpers import Helpers
from ..utils.logger import Logger


class UserService:
    @staticmethod
    def get_user_profile(user_id) -> dict:
        try:
            user = UserRepository.find_user_by_id(user_id)
            if not user:
                raise UserDoesNotExistError("user does not exist")
            user_data = {
                "user_id": user.get("user_id"),
                "email": user.get("email"),
                "status": user.get("status"),
                "reset_token": user.get("reset_token"),
                "created_at": user.get("created_at"),
                "updated_at": user.get("updated_at"),
            }

            return user_data
        except Exception:
            raise GenericDatabaseError("error occurred while finding user")

    @staticmethod
    def get_user(email, password) -> dict:
        user = UserRepository.find_user_by_mail(email)
        if not user:
            Logger.warn(f"user not found for email {email}")
            raise InvalidCredentialsError("Invalid email")
        if user["status"] != 1:
            Logger.warn(f"user not verified for {email}")
            raise InvalidLoginAttemptError("Your account is not verified")
        if user["is_deactivated"] == 1:
            Logger.warn(f"user {email} is deactivated")
            raise InvalidLoginAttemptError("You account is deactivated")
        if not Security.check_password(password, user["hash"]):
            Logger.warn(f"Invalid password for user {email}")
            raise InvalidCredentialsError("Invalid email or password")

        return user

    @staticmethod
    def register_user(username, email, password) -> dict:
        user = UserRepository.find_user_by_mail(email)
        if user:
            Logger.warn(f"User already exist for email {email}")
            raise UserExistError("user already exists")
        password_hash = Security.hash_password(password)
        status = 0
        result = UserRepository.add_user(email, password_hash, status)
        if result < 1:
            Logger.error("error adding user to db")
            raise GenericDatabaseError("error occured while adding user")
        return {"rows_affected": result}

    @staticmethod
    def store_verification_code(email, code) -> bool:
        return BaseCache.store_verification_code(email, code)

    @staticmethod
    def verify_account(email, code) -> bool:
        try:
            has_code = BaseCache.verify_code(email, code)
            active = 1
            if has_code:
                return UserRepository.update_user_status(email, active) > 1
            return False
        except Exception as e:
            Logger.exception(str(e))
            raise GenericDatabaseError(str(e))

    @staticmethod
    def store_reset_token(email: str) -> dict:
        try:
            token = Helpers.generate_reset_token(email)
            if not token:
                raise GenericGenerateResetTokenError(
                    "An error occured while generating reset token"
                )
            data = {
                "token": token,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            is_held = BaseCache.hold_reset_token(email, data)
            if not is_held:
                Logger.error(
                    "An error occurred while storing reset token in redis")
                raise GenericRedisError(
                    "An error occurred while storing reset token in redis"
                )
            if not UserRepository.store_reset_token(email, token) > 0:
                Logger.error("An error occured while storing reset token")
                raise GenericDatabaseError(
                    "An error occured while storing reset token")
            return data
        except Exception as e:
            Logger.exception(str(e))
            raise GenericDatabaseError(str(e))

    @staticmethod
    def get_reset_token(email: str, submitted_token: str) -> str:
        try:
            tkn = BaseCache.retrieve_reset_token(email, submitted_token)
            if not tkn:
                data = UserRepository.get_reset_token(email)
                if not data:
                    Logger.error(f"no token found for {email}")
                    raise InvalidPasswordResetError("No reset token found")
                if data["reset-token"] != submitted_token:
                    Logger.error(f"Reset token do not match for {email}")
                    raise InvalidPasswordResetError(
                        "Wrong password reset token")
                if not Helpers.compare_token_time(data):
                    Logger.warn("The reset token has expired")
                    raise InvalidPasswordResetError(
                        "The reset token has expired")
                return data["reset-token"]
            return tkn
        except Exception as e:
            Logger.exception(str(e))
            raise GenericDatabaseError(str(e))

    @staticmethod
    def change_password(email: str, password: str) -> bool:
        try:
            hashed_password = Security.hash_password(password)
        except Exception as e:
            Logger.exception(str(e))
            raise GenericPasswordHashError(
                "There is a problem generating password hash"
            )

        try:
            return UserRepository.update_password(email, hashed_password) > 0
        except Exception as e:
            Logger.exception(str(e))
            raise GenericDatabaseError(str(e))
