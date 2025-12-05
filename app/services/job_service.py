from typing import Any

from ..repositories.jobs_repository import JobRepository
from ..utils.exceptions import (
    GenericDatabaseError,
    InvalidLoginAttemptError
)
from ..utils.logger import Logger
from ..utils.security import Security


class JobService:
    @staticmethod
    def add_job(data: dict[str, str]) -> int | None:

        try:
            if not isinstance(data, dict):
                return None

            # 1. Get the token and check if it is valid
            token = data['token']
            decoded = Security.decode_jwt_token(token)

            # 2. Compare the decoded tokens id with the provided id
            token_admin_id = decoded['profile_id']
            if not token_admin_id:
                Logger.warn(
                    f'Provided token {token} is not related to {decoded['email']}')
                raise InvalidLoginAttemptError(
                    "Unauthorized job creation attempt")

            # 3. Add admin_id into the data
            data['admin_id'] = token_admin_id

            # 4. Attempt to insert the job into the jobs table
            row_id = JobRepository.insert_job(data)
            if row_id is None:
                Logger.warn(f"Errr while creating {data} job")
                return None

            if row_id < 1:
                Logger.warn(f"Job {data} was not added")
                return None
            return row_id
        except Exception as e:
            Logger.warn(f"Job {data} was not added because of {str(e)}")
            raise GenericDatabaseError(f"Error because of {str(e)}")

    @staticmethod
    def fetch_jobs(page: int, limit: int) -> dict:
        try:
            offset = (page - 1) * limit
            jobs = JobRepository.get_jobs(limit, offset)

            return {
                'page': page,
                'limit': limit,
                'count': len(jobs),
                'jobs': jobs
            }
        except Exception as e:
            Logger.warn(f'Error occurred {str(e)}')
            raise GenericDatabaseError(f'{str(e)}')

    @staticmethod
    def fetch_job(job_id: int) -> dict:
        try:
            return JobRepository.get_job(job_id)
        except Exception as e:
            Logger.warn(f'Error occurred {str(e)}')
            raise GenericDatabaseError(f'{str(e)}')

    @staticmethod
    def update_job(job_id: int, token: str, data: dict[str, Any]) -> dict:
        try:
            decoded = Security.decode_jwt_token(token)
            admin_id = decoded['profile_id']
            if not admin_id:
                Logger.warn(
                    f'Provided token {token} is not related to {decoded['email']}')
                raise InvalidLoginAttemptError(
                    "Unauthorized job update attempt")

            affected_row = JobRepository.update_job(job_id, admin_id, data)
            if affected_row == 0:
                raise GenericDatabaseError(
                    {'msg': f'No job found with id {job_id}'})
            return JobRepository.get_job(job_id)
        except Exception as e:
            Logger.warn(f'An error occurred {str(e)}')
            raise GenericDatabaseError(f'{str(e)}')
