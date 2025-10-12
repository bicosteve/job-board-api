from ..repositories.user_repository import UserRepository
from ..utils.security import Security
from ..utils.exceptions import (
    InvalidCredentialsError,
    UserExistError,
    GenericDatabaseError,
)


class UserService:
    @staticmethod
    def get_user_profile(user_id):
        user_profile = UserRepository.find_user_by_id(user_id)
        if not user_profile:
            raise GenericDatabaseError("error occured while finding user")
        return user_profile

    @staticmethod
    def get_user(email, password):
        user = UserRepository.find_user_by_mail(email)
        if not user:
            raise InvalidCredentialsError("Invalid email")
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
