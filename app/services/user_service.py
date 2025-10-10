from ..repositories.user_repository import UserRepository


class UserService:
    @staticmethod
    def get_user(user_id):
        return UserRepository.find_user(user_id)
