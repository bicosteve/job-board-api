from ..repositories.jobs_repository import JobRepository
from ..repositories.base_cache import BaseCache
from ..utils.exceptions import (
    GenericDatabaseError,
    InvalidLoginAttemptError,
    GenericRedisError
)
from ..utils.helpers import Helpers
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
                raise InvalidLoginAttemptError("Unauthorized login attempt")

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
