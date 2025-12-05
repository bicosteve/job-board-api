from ..utils.logger import Logger
from ..utils.security import Security
from ..utils.exceptions import (
    InvalidCredentialsError,
    GenericDatabaseError
)
from ..repositories.applications_repository import ApplicationRepository


class ApplicationService:

    @staticmethod
    def make_application(token: str, data: dict) -> bool:
        try:
            decoded = Security.decode_jwt_token(token)
            if not decoded:
                Logger.warn(f'Could not decode token {token}')
                raise InvalidCredentialsError(
                    f'Could not decode token {token}')

            user_id = decoded['profile_id']
            if not user_id:
                Logger.warn(f'Failed to get user_id from {decoded}')
                raise ValueError(f'Failed to get user_id from {decoded}')

            if not isinstance(data, dict):
                Logger.warn(
                    f'Invalid payload {data}. Wants object received list or None')
                raise ValueError(
                    f'Invalid payload {data}. Wants object received list or None')

            return ApplicationRepository.create_application(user_id, data) > 0
        except Exception as e:
            raise GenericDatabaseError(f'Error occurred {str(e)}')

    @staticmethod
    def get_all_job_applications(job_id: int, limit: int, page: int) -> dict:
        try:
            offset = (page - 1) * limit
            applications = ApplicationRepository.get_jobs_applications(
                job_id, limit, offset)

            return {
                'page': page,
                'limit': limit,
                'count': len(applications),
                'applications': applications
            }
        except Exception as e:
            Logger.warn(f'Error occurred {str(e)}')
            raise GenericDatabaseError(f'Error occurred {str(e)}')

    @staticmethod
    def get_job_application(token: str, job_id: int) -> dict:
        try:
            decoded = Security.decode_jwt_token(token)
            if not decoded:
                Logger.warn(f'Could not decode token {token}')
                raise InvalidCredentialsError(
                    f'Could not decode token {token}')

            user_id = decoded['profile_id']
            if not user_id:
                Logger.warn(f'Failed to get user_id from {decoded}')
                raise ValueError(f'Failed to get user_id from {decoded}')

            return ApplicationRepository.get_user_application(user_id, job_id)
        except Exception as e:
            Logger.warn(f'Error occurred {str(e)}')
            raise GenericDatabaseError(f'Error occurred {str(e)}')

    @staticmethod
    def list_users_applications(token: str) -> list:
        try:
            decoded = Security.decode_jwt_token(token)
            if not decoded:
                Logger.warn(f'Could not decode token {token}')
                raise InvalidCredentialsError(
                    f'Could not decode token {token}')

            user_id = decoded['profile_id']
            if not user_id:
                Logger.warn(f'Failed to get user_id from {decoded}')
                raise ValueError(f'Failed to get user_id from {decoded}')

            return ApplicationRepository.get_user_applications(user_id)
        except Exception as e:
            Logger.warn(f'Error occurred {str(e)}')
            raise GenericDatabaseError(f'Error occurred {str(e)}')

    @staticmethod
    def update_an_application(token: str, app_id: int, status: int) -> bool:
        try:
            decoded = Security.decode_jwt_token(token)
            if not decoded:
                Logger.warn(f'Could not decode token {token}')
                raise InvalidCredentialsError(
                    f'Could not decode token {token}')

            admin_id = decoded['profile_id']
            if not admin_id:
                Logger.warn(f'Failed to get user_id from {decoded}')
                raise ValueError(f'Failed to get user_id from {decoded}')

            return ApplicationRepository.update_application(
                app_id, admin_id, status) > 0
        except Exception as e:
            Logger.warn(f'Error occurred {str(e)}')
            raise GenericDatabaseError(f'Error occurred {str(e)}')
