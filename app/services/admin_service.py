from datetime import datetime

from ..repositories.admin_repository import AdminRepository
from ..utils.security import Security
from ..utils.exceptions import (
    InvalidCredentialsError,
    UserExistError,
    GenericDatabaseError,
    InvalidLoginAttemptError,
    GenericPasswordHashError,
    UserDoesNotExistError
)
from ..utils.helpers import Helpers
from ..utils.logger import Logger


class AdminService:

    @staticmethod
    def get_admin_profile(id: int) -> dict[str, str] | None:
        admin = AdminRepository.find_admin_by_id(id)
        if admin is None:
            return None
        return admin

    @staticmethod
    def get_admin_user(email: str, password: str) -> dict[str, str] | None:
        Logger.info(f"Finding admin user with email {email}")
        admin = AdminRepository.find_admin_by_email(email)
        if admin is None:
            Logger.warn(f"Admin user with email {email} not found")
            raise UserDoesNotExistError(f"User with email {email} not found")

        # 1. Compare passwords
        hashed_password = admin['password_hash']
        Logger.info(f"Checking password for admin user {email}")

        if not Security.check_password(password, hashed_password):
            Logger.warn(f"Invalid password for user {email}")
            raise InvalidCredentialsError("Password or email do not match")

        # 2. Check if has active status
        Logger.info(f"Checking admin user with {email} status")

        if int(admin["is_deactivated"]) != 1:
            Logger.warn(f"Admin user with {email} status not active")
            raise InvalidLoginAttemptError("User is not active")

        # 3. Generate login token and send to admin controller
        Logger.info(f"Creating jwt token for admin user with email {email}")
        token = Security.create_jwt_token(
            str(admin['id']), str(admin['email']))
        return {"msg": "success", "token": token}

    @staticmethod
    def add_admin_user(data: dict[str, str]) -> dict[str, int] | None:
        if isinstance(data, dict):

            # 0. Check if the user exists and if yes raise UserExistError()
            admin_user = AdminRepository.find_admin_by_email(data['email'])
            Logger.info("Logging admin user" + str(admin_user))
            if admin_user is not None:
                raise UserExistError(
                    f"User with {data['email']} already exists")

            # 1. Get/Generate username
            username = data['email'].split("@")[0]

            # 2. Generate password hash
            password_hash = Security.hash_password(data['password'])

            # 3. Package the data into an object/dict and send to repo
            obj = {
                "email": data['email'],
                "username": username,
                "password_hash": password_hash
            }

            Logger.info(f"Generated admin object {obj}")

            # 4. Send to Admin repository for further processing
            Logger.info(f"Adding admin user to database")
            res = AdminRepository.add_admin(obj)
            if res is None:
                Logger.warn("Error adding admin user")
                return None

            if res < 1:
                Logger.warn(f"Error adding admin user with {res}")
                raise GenericDatabaseError(
                    "An error occured while adding user")
            return {"rows": res}
        return None
