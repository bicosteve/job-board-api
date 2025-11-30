from datetime import datetime
from typing import Dict, Any, Optional, Union, List

from flask import jsonify, make_response
from flask_restful import Resource, request
from marshmallow import ValidationError
from jwt import ExpiredSignatureError, InvalidTokenError
from flasgger import swag_from


from ..services.user_service import UserService
from ..schemas.user import (
    RegisterSchema,
    LoginSchema,
    VerifyAccountSchema,
    ResetPasswordSchema,
    RequestResetPasswordSchema,
)
from ..utils.exceptions import (
    InvalidCredentialsError,
    UserExistError,
    GenericDatabaseError,
)
from ..utils.security import Security
from ..utils.helpers import Helpers
from ..utils.logger import Logger


class RegisterUserController(Resource):
    register_schema = RegisterSchema()

    @swag_from("../docs/register.yml")
    def post(self):
        data: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None
        try:
            json_data = request.get_json()
            if json_data is None:
                raise ValueError("No JSON data provided")
            elif isinstance(json_data, dict):
                data = RegisterUserController.register_schema.load(json_data)
            else:
                raise ValueError(
                    f"Expected JSON object, got {type(json_data)}")
        except ValidationError as e:
            Logger.warn(f"Validation failed during registration {str(e)}")
            return {"error": str(e)}, 400

        if isinstance(data, dict):
            email = data["email"]
            password = data["password"]
            username = data["email"].split("@")[0]
        else:
            raise ValidationError("Expected dict, got list or None")

        try:
            Logger.info(f"Attempting to register user: {email}")
            user = UserService.register_user(username, email, password)

            if not user or user.get("rows_affected", 0) < 1:
                Logger.error(f"User registration failed for {email}")
                return {"msg": "User registration failed"}, 500

            code = Helpers.generate_verification_code()
            if not UserService.store_verification_code(email, code):
                Logger.error(f"Failed to store verification code for {email}")
                return {"msg": "Verification code error"}, 500

            Logger.info(f"User registered successfully: {email}")
            return {
                "msg": "user created",
                "verification_code": code,
                "email": email,
            }, 201

        except UserExistError as e:
            Logger.warn(f"User already exists: {email}-{e}")
            return {"user_error": str(e)}, 400

        except GenericDatabaseError as e:
            Logger.error(
                f"Database error during registration for {email}-{str(e)}")
            return {"db_error": str(e)}, 500

        except Exception as e:
            Logger.exception(
                f"Unexpected error during registration for {email} : {str(e)}"
            )
            return {"generic_error": "An unexpected error occurred"}, 500


class LoginUserController(Resource):
    login_schema = LoginSchema()

    @swag_from("../docs/login.yml")
    def post(self):
        try:
            data = LoginUserController.login_schema.load(request.get_json())
        except ValidationError as e:
            Logger.warn(f"Failed payload validation on login {str(e)}")
            return {"error": str(e)}, 400

        try:
            if isinstance(data, dict):
                email = data['email']
                password = data['password']
            else:
                raise ValueError("Expected dict, got None or list")

            user = UserService.get_user(email, password)
            error = f"Failed to get user with email {data["email"]} on login"
            if not user:
                Logger.warn(error)
                return {"msg": error}, 404

            if "token" not in user or not user['token']:
                Logger.error("Token generation failed during login")
                return {"msg": "Token generation failed"}, 500

            response = make_response(
                jsonify(
                    {
                        "msg": "Login success",
                        "token": user['token']
                    }
                ),
                200,
            )
            Logger.info(f"Login success {response}")
            return response
        except GenericDatabaseError as e:
            Logger.error(f"DB error during login {str(e)}")
            return {"db_error": str(e)}, 500
        except InvalidCredentialsError as e:
            Logger.warn(f"Invalid credentials error {str(e)}")
            return {"credentials_error": str(e)}, 401
        except Exception as e:
            Logger.exception(f"Unexpected error during login {str(e)}")
            return {"generic_error": str(e)}, 500


class UserProfileController(Resource):
    """Get user profile"""

    @swag_from("../docs/get_profile.yml")
    def get(self):
        """Gets user profile and return the details"""
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            Logger.warn("Authorization missing header")
            return {"error": "Authorization missing header"}, 401
        if not auth_header.startswith("Bearer "):
            Logger.warn("Invalid authorization header format")
            return {"error": "Invalid authorization header format"}, 401

        token = auth_header.split(" ")[1]

        try:
            payload = Security.decode_jwt_token(token)
            profile_id = payload.get("profile_id", "")

            if not profile_id:
                Logger.warn("Profile id not found for user")
                return {"error": "Invalid payload"}, 401

            user = UserService.get_user_profile(profile_id)
            if not user:
                Logger.warn(f"No user with profile {profile_id}")
                return {"error": "User not found"}, 404

            Logger.info(f"Returning profile {user}")
            return user, 200

        except ExpiredSignatureError as e:
            Logger.warn(f"Expired token signature {str(e)}")
            return {"error": "token has expired"}, 401
        except InvalidTokenError as e:
            Logger.warn(f"Invalid token signature {str(e)}")
            return {"error": "Invalid token"}, 401
        except Exception as e:
            Logger.exception(f"Unexpected error occured {str(e)}")
            return {"error": str(e)}, 500


class CheckAppHealthController(Resource):
    """Get the app status"""

    @swag_from("../docs/get_health.yml")
    def get(self):
        """Get the status of the app"""

        now = datetime.now()

        return {
            "data": {
                "time": str(now.time()),
                "date": str(now.date()),
                "now": now.strftime("%Y-%m-%d %H:%M:%S"),
                "msg": "App is running successfully",
            }
        }, 200


class VerifyUserAccountController(Resource):
    verify_account_schema = VerifyAccountSchema()

    @swag_from("../docs/verify_account.yml")
    def post(self):
        try:
            data = VerifyUserAccountController.verify_account_schema.load(
                request.get_json())
        except ValidationError as e:
            Logger.warn(f"An error occured while validating payload {str(e)}")
            return {"validation_error": str(e)}, 400

        if isinstance(data, dict):
            email = data["email"]
            code = data["verification_code"]
        else:
            raise ValueError("Expected a dict, got None or list")

        try:
            is_verified = UserService.verify_account(email, code)
            if not is_verified:
                Logger.warn(f"Error while verifying account {email}")
                return {"error": "error while verifying account"}, 500
            return {"msg": "account verification success"}, 200
        except UserExistError as e:
            Logger.warn(f"{str(e)}")
            return {"user_error": str(e)}, 400
        except GenericDatabaseError as e:
            Logger.warn(f"DB error {str(e)} during account verification")
            return {"db_error": str(e)}, 500
        except Exception as e:
            Logger.exception(f"Unexpected error occurred {str(e)}")
            return {"generic_error": str(e)}, 500


class RequestUserPasswordResetController(Resource):
    request_reset_password_schema = RequestResetPasswordSchema()

    @swag_from("../docs/request_reset_code.yml")
    def post(self):
        try:
            data = RequestUserPasswordResetController.request_reset_password_schema.load(
                request.get_json()
            )
        except ValidationError as e:
            Logger.warn(f"Error while validating payload {str(e)}")
            return {"validation_error": str(e)}, 400

        if isinstance(data, dict):
            email = data['email']
        else:
            raise ValueError("Expected dict, got None or list")

        try:
            token_data = UserService.store_reset_token(email)
            if not token_data:
                Logger.warn("An error occurred while storing reset token")
                return {"error": "An error occurred while storing reset token"}, 500
            return {"data": token_data}, 201
        except Exception as e:
            Logger.exception(f"Unexpected error {str(e)} occurred")
            return {"generic_error": str(e)}, 500


class ResetUserPasswordController(Resource):
    reset_password_schema = ResetPasswordSchema()

    @swag_from("../docs/password_reset.yml")
    def post(self):
        token = str(request.args.get("token"))
        if len(token) < 1 or None:
            Logger.warn("No reset token provided in the request")
            return {"validation_error": "Token is required"}

        try:
            data = ResetUserPasswordController.reset_password_schema.load(
                request.get_json())
        except ValidationError as e:
            Logger.warn(f"Error validating the payload {str(e)}")
            return {"validation_error": f"payload error {str(e)}"}
        except Exception as e:
            Logger.exception(f"Unexpected error {str(e)} occurred")
            return {"generic_error": str(e)}, 500

        if isinstance(data, dict):
            password = data['password']
        else:
            raise ValueError("Expected dict,got None or List")

        try:
            email = Helpers.verify_reset_token(token, 3600)
            if email is None:
                Logger.warn("Cannot verify reset token for user")
                return {"error": "Cannot verify reset token"}, 400

            if not UserService.change_password(email, password):
                Logger.error(f"Failed to reset password for {email}")
                return {"error": f"Failed to reset password for {email}"}, 500
            return {"msg": "Password changed successfully"}, 200
        except Exception as e:
            Logger.exception(f"Unexpected error {str(e)} occurred")
            return {"generic_error": str(e)}, 500
