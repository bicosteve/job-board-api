from ..services.notification_service import NotificationService
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

            result = ApplicationRepository.create_application(user_id, data)
            if result < 1:
                return False

            info = ApplicationRepository.get_job_info_for_notification(data['job_id'])
            if isinstance(info, dict) and info.get('job_title'):
                NotificationService.notify_applicant_of_submission(
                    decoded['email'],
                    info.get('job_title', 'your role'),
                    info.get('company_name', 'the hiring team')
                )
                if info.get('employer_email'):
                    NotificationService.notify_employer_of_new_application(
                        info.get('employer_email'),
                        info.get('job_title', 'a role'),
                        decoded['email']
                    )
            return True
        except Exception as e:
            raise GenericDatabaseError(f'Error occurred {str(e)}')

    @staticmethod
    def get_all_job_applications(token: str, job_id: int, limit: int, page: int) -> dict:
        try:
            decoded = Security.decode_jwt_token(token)
            if not decoded:
                Logger.warn(f'Could not decode token {token}')
                raise InvalidCredentialsError(
                    f'Could not decode token {token}')

            admin_id = decoded['profile_id']
            if not admin_id:
                raise ValueError('Admin id missing from token')

            offset = (page - 1) * limit
            applications = ApplicationRepository.get_jobs_applications(
                job_id, limit, offset, admin_id)

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

            updated = ApplicationRepository.update_application(app_id, admin_id, status) > 0
            if not updated:
                return False

            details = ApplicationRepository.get_application_details(app_id)
            if details and details.get('applicant_email'):
                NotificationService.notify_applicant_status_change(
                    details['applicant_email'],
                    details.get('job_title', 'your application'),
                    status,
                    details.get('company_name')
                )
            return True
        except Exception as e:
            Logger.warn(f'Error occurred {str(e)}')
            raise GenericDatabaseError(f'Error occurred {str(e)}')
