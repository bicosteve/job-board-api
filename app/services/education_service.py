from ..repositories.education_repository import EducationRepository
from ..utils.logger import Logger
from ..utils.security import Security
from ..utils.exceptions import (
    GenericGenerateAuthTokenError,
    GenericDatabaseError
)


class EducationService:
    @staticmethod
    def create_education(token: str, payload: dict[str, str]):
        try:
            if not isinstance(payload, dict):
                Logger.warn(f'Provided data {payload} is not valid object')
                raise ValueError(
                    f'Provided data {payload} is not valid object')

            decoded = Security.decode_jwt_token(token)
            if not decoded:
                Logger.warn(f'Provided token {token} is not valid')
                raise GenericGenerateAuthTokenError(
                    f'Provided token {token} is not valid')

            user_id = decoded['profile_id']
            if not user_id:
                Logger.warn(f'Failed to get user_id from {decoded}')
                raise GenericGenerateAuthTokenError(
                    f'Failed to get user_id from {decoded}')

            affected_row = EducationRepository.add_education(user_id, payload)
            if affected_row < 1:
                Logger.warn(
                    f'Failed to create education for {user_id} with  {payload}')
                raise GenericDatabaseError(
                    f'Failed to create education for {user_id} with  {payload}')
            return affected_row
        except Exception as e:
            raise Exception(f'error becasue of {str(e)}')
