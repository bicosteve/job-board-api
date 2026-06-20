from typing import cast

from flasgger import swag_from
from flask import jsonify, make_response
from flask_restful import Resource, request
from marshmallow import ValidationError

from ..extensions.limiter import auth_limits, limiter
from ..schemas.admin import LoginAdminSchema, RegisterAdminSchema, VerifyAdminSchema
from ..services.admin_service import AdminService
from ..services.notification_service import NotificationService
from ..utils.exceptions import (
    GenericDatabaseError,
    InvalidCredentialsError,
    InvalidLoginAttemptError,
    UserDoesNotExistError,
    UserExistError,
)
from ..utils.helpers import Helpers
from ..utils.logger import Logger


class RegisterAdminController(Resource):

    @swag_from("../docs/register_admin.yml")
    def post(self):
        try:
            register_schema = RegisterAdminSchema()
            Logger.info("Validating admin user register payload")
            data = register_schema.load(request.get_json())
            if not isinstance(data, dict):
                Logger.warn("Provided data is not object.")
                return {"msg": "Expected an object got None"}, 400
            Logger.info(f"Attempting to register user {data['email']}")
            code = Helpers.generate_verification_code()

            # Add verification code to the data payload
            data["verification_code"] = code

            res = AdminService.add_admin_user(data)
            if res is None:
                Logger.warn("An error occured while adding admin.")
                return {"msg": "error adding admin user"}, 500
            if res["rows"] < 1:
                Logger.warn("Admin not registered")
                return {"msg": "Admin not registered"}, 500

            if not NotificationService.send_verification_code(
                data["email"], code, is_admin=True
            ):
                Logger.warn(
                    f"Email delivery may have failed for admin verification to {data['email']}"
                )

            return {"msg": "Admin created", "verification_code": code}, 201
        except ValidationError as e:
            return {"error": str(e.messages)}, 400
        except UserExistError as e:
            return {"error": f"{str(e)}"}, 409
        except GenericDatabaseError as e:
            return {"error": f"{str(e)}"}, 500


class LoginAdminController(Resource):

    decorators = [limiter.limit(auth_limits)]

    @swag_from("../docs/login_admin.yml")
    def post(self):

        try:
            login_schema = LoginAdminSchema()
            Logger.info("Validating login admin user payload")
            data = cast(dict[str, str], login_schema.load(request.get_json()))

            admin = AdminService.get_admin_user(data["email"], data["password"])

            if not isinstance(admin, dict):
                Logger.warn("Problem with getting admin user")
                return {"error": "The problem with getting user"}, 500

            response = make_response(jsonify(admin), 200)

            return response
        except ValidationError as err:
            Logger.warn(f"Validation failed: {err.messages}")
            return {"error": err.messages}, 400
        except InvalidLoginAttemptError as e:
            return {"error": str(e)}, 400
        except InvalidCredentialsError as e:
            return {"error": str(e)}, 401
        except UserDoesNotExistError as e:
            return {"error": str(e)}, 404
        except GenericDatabaseError as e:
            return {"db_error": str(e)}, 500


class VerifyAdminAccountController(Resource):

    decorators = [limiter.limit(auth_limits)]

    @swag_from("../docs/verify_admin_account.yml")
    def post(self):

        try:
            verify_schema = VerifyAdminSchema()
            data = verify_schema.load(request.get_json())
            if not isinstance(data, dict):
                return {"error": f"Paylaod {data} is invalid"}

            obj = {
                "email": data["email"],
                "active_status": 1,
                "verification_code": data["verification_code"],
            }

            res = AdminService.verify_admin_user(obj)
            if res is None:
                Logger.warn(f"An error occurred while verifiying {data['email']}")
                return {"error": "An error occurred during verification"}, 500

            return {"msg": "account verified"}, 200
        except (ValidationError, ValueError, TypeError) as err:
            Logger.warn(f"Validation failed {err}")
            return {"err": str(err)}, 400
        except GenericDatabaseError as e:
            return {"db_error": str(e)}, 500
