from ..repositories.user_repository import UserRepository
from ..repositories.user_cache import UserCache
from ..utils.security import Security
from ..utils.exceptions import (
    InvalidCredentialsError,
    UserExistError,
    GenericDatabaseError,
    InvalidLoginAttemptError,
)


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
            raise InvalidCredentialsError("Invalid email")
        if user["status"] != 1:
            raise InvalidLoginAttemptError("Your account is not verified")
        if not Security.check_password(password, user["hash"]):
            raise InvalidCredentialsError("Invalid email or password")
        return user

    @staticmethod
    def register_user(username, email, password):
        exists = UserRepository.find_user_by_mail(email)
        if exists:
            raise UserExistError("user already exists")
        hash = Security.hash_password(password)
        status = 0
        result = UserRepository.add_user(email, hash, status)
        if not result:
            raise GenericDatabaseError("error occured while adding user")
        return {"rows_affected": result}

    @staticmethod
    def store_verification_code(email, code) -> bool:
        is_stored = UserCache.store_verification_code(email, code)
        return is_stored

    @staticmethod
    def verify_account(email, code) -> bool:
        try:
            if not UserCache.verify_code(email, code):
                return False
            return UserRepository.update_user_status(email) > 0
        except Exception as e:
            raise GenericDatabaseError(str(e))
