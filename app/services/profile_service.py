from ..utils.security import Security
from ..utils.logger import Logger
from ..repositories.profile_repository import ProfileRepository
from ..utils.exceptions import (
    GenericDatabaseError,
    InvalidCredentialsError
)


class ProfileService:
    @staticmethod
    def create_profile(token: str, payload: dict[str, str]) -> int:
        try:
            if not isinstance(payload, dict):
                raise ValueError(f'Provided payload {payload} is not valid')
            decoded = Security.decode_jwt_token(token)
            if not decoded:
                Logger.warn(f'Provided token {token} is invalid')
                raise InvalidCredentialsError("Provided token is invalid")
            user_id = decoded['profile_id']
            if not user_id:
                Logger.warn(f'Error getting user_id from {token}')
                raise InvalidCredentialsError(
                    f'Error getting user_id from {token}')

            row = ProfileRepository.add_profile(user_id, payload)
            if row < 1:
                Logger.warn(f'Profile for {payload} not created')
                return 0
            return 1
        except Exception as e:
            raise GenericDatabaseError(
                f'An error occurred because of {str(e)}')

    @staticmethod
    def get_profile(token: str) -> dict:
        try:
            decoded = Security.decode_jwt_token(token)
            if not decoded:
                Logger.warn(f'Provided token {token} is invalid')
                raise InvalidCredentialsError("Provided token is invalid")
            user_id = decoded['profile_id']
            if not user_id:
                Logger.warn(
                    f'Did not manage to get user_id from token {token}')
                raise InvalidCredentialsError("Provided token is invalid")

            profile = ProfileRepository.get_profile(user_id)
            if not profile:
                raise Exception('Failed to get profile from db')
            return profile
        except Exception as e:
            raise Exception(f'Problem {str(e)} while getting profile')
