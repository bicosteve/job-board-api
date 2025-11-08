from datetime import datetime

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
from ..utils.logger import Loggger


class UserRegister(Resource):
    register_schema = RegisterSchema()

    @swag_from("../docs/register.yml")
    def post(self):
        try:
            data = UserRegister.register_schema.load(request.get_json())
        except ValidationError as e:
            Loggger.warn(f"Validation failed during registration {str(e)}")
            return {"error": str(e)}, 400

        email = data["email"]
        password = data["password"]
        username = data["email"].split("@")[0]

        try:
            Loggger.info(f"Attempting to register user: {email}")
            user = UserService.register_user(username, email, password)

            if not user or user.get("rows_affected", 0) < 1:
                Loggger.error(f"User registration failed for {email}")
                return {"msg": "User registration failed"}, 500

            code = Helpers.generate_verification_code()
            if not UserService.store_verification_code(email, code):
                Loggger.error(f"Failed to store verification code for {email}")
                return {"msg": "Verification code error"}, 500

            Loggger.info(f"User registered successfully: {email}")
            return {
                "msg": "user created",
                "verification_code": code,
                "email": email,
            }, 201

        except UserExistError as e:
            Loggger.warn(f"User already exists: {email}-{e}")
            return {"user_error": str(e)}, 400

        except GenericDatabaseError as e:
            Loggger.error(f"Database error during registration for {email}-{str(e)}")
            return {"db_error": str(e)}, 500

        except Exception as e:
            Loggger.exception(
                f"Unexpected error during registration for {email} : {str(e)}"
            )
            return {"generic_error": "An unexpected error occurred"}, 500


class UserLogin(Resource):
    login_schema = LoginSchema()

    @swag_from("../docs/login.yml")
    def post(self):
        try:
            data = UserLogin.login_schema.load(request.get_json())
        except ValidationError as e:
            Loggger.warn(f"Failed payload validation on login {str(e)}")
            return {"error": str(e)}, 400

        email = data["email"]
        password = data["password"]

        try:
            user = UserService.get_user(email, password)
            error = f"Failed to get user with email {email} on login"
            if not user:
                Loggger.warn(error)
                return {"msg": error}, 404
            token = Security.create_jwt_token(user["user_id"], user["email"])
            if token is None:
                Loggger.warn(f"Failed to generate token for {email}")
                return {"msg": "Token generation error"}, 500
            response = make_response(
                jsonify(
                    {
                        "msg": "Login success",
                        "token": token,
                    }
                ),
                200,
            )
            Loggger.info(f"Login success {response}")
            response.headers["Authorization"] = f"Bearer {token}"
            return response
        except GenericDatabaseError as e:
            Loggger.error(f"DB error during login {str(e)}")
            return {"db_error": str(e)}, 500
        except InvalidCredentialsError as e:
            Loggger.warn(f"Invalid credentials error {str(e)}")
            return {"credentials_error": str(e)}, 401
        except Exception as e:
            Loggger.exception(f"Unexpected error during login {str(e)}")
            return {"generic_error": str(e)}, 500


class UserProfile(Resource):
    """Get user profile"""

    @swag_from("../docs/get_profile.yml")
    def get(self):
        """Gets user profile and return the details"""
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            Loggger.warn("Authorization missing header")
            return {"error": "Authorization missing header"}, 401
        if not auth_header.startswith("Bearer "):
            Loggger.warn("Invalid authorization header format")
            return {"error": "Invalid authorization header format"}, 401

        token = auth_header.split(" ")[1]

        try:
            payload = Security.decode_jwt_token(token)
            profile_id = payload.get("profile_id", "")

            if not profile_id:
                Loggger.warn("Profile id not found for user")
                return {"error": "Invalid payload"}, 401

            user = UserService.get_user_profile(profile_id)
            if not user:
                Loggger.warn(f"No user with profile {profile_id}")
                return {"error": "User not found"}, 404

            Loggger.info(f"Returning profile {user}")
            return user, 200

        except ExpiredSignatureError as e:
            Loggger.warn(f"Expired token signature {str(e)}")
            return {"error": "token has expired"}, 401
        except InvalidTokenError as e:
            Loggger.warn(f"Invalid token signature {str(e)}")
            return {"error": "Invalid token"}, 401
        except Exception as e:
            Loggger.exception(f"Unexpected error occured {str(e)}")
            return {"error": str(e)}, 500


class AppHealthCheck(Resource):
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


class UserVerifyAccount(Resource):
    verify_account_schema = VerifyAccountSchema()

    @swag_from("../docs/verify_account.yml")
    def post(self):
        try:
            data = UserVerifyAccount.verify_account_schema.load(request.get_json())
        except ValidationError as e:
            Loggger.warn(f"An error occured while validating payload {str(e)}")
            return {"validation_error": str(e)}, 400

        email = data.get("email")
        code = data.get("verification_code")

        try:
            is_verified = UserService.verify_account(email, code)
            if not is_verified:
                Loggger.warn(f"Error while verifying account {email}")
                return {"error": "error while verifying account"}, 500
            return {"msg": "account verification success"}, 200
        except UserExistError as e:
            Loggger.warn(f"{str(e)}")
            return {"user_error": str(e)}, 400
        except GenericDatabaseError as e:
            Loggger.warn(f"DB error {str(e)} during account verification")
            return {"db_error": str(e)}, 500
        except Exception as e:
            Loggger.exception(f"Unexpected error occurred {str(e)}")
            return {"generic_error": str(e)}, 500


class ResetPasswordRequest(Resource):
    request_reset_password_schema = RequestResetPasswordSchema()

    @swag_from("../docs/request_reset_code.yml")
    def post(self):
        try:
            data = ResetPasswordRequest.request_reset_password_schema.load(
                request.get_json()
            )
        except ValidationError as e:
            Loggger.warn(f"Error while validating payload {str(e)}")
            return {"validation_error": str(e)}, 400

        try:
            email = data.get("email", "")
            token_data = UserService.store_reset_token(email)
            if not token_data:
                Loggger.warn("An error occurred while storing reset token")
                return {"error": "An error occurred while storing reset token"}, 500
            return {"data": token_data}, 201
        except Exception as e:
            Loggger.exception(f"Unexpected error {str(e)} occurred")
            return {"generic_error": str(e)}, 500


class AccountPasswordReset(Resource):
    reset_password_schema = ResetPasswordSchema()

    @swag_from("../docs/password_reset.yml")
    def post(self):
        token = request.args.get("token")
        if len(token) < 1:
            Loggger.warn("No reset token provided in the request")
            return {"validation_error": "Token is required"}

        try:
            data = AccountPasswordReset.reset_password_schema.load(request.get_json())
        except ValidationError as e:
            Loggger.warn(f"Error validating the payload {str(e)}")
            return {"validation_error": f"payload error {str(e)}"}
        except Exception as e:
            Loggger.exception(f"Unexpected error {str(e)} occurred")
            return {"generic_error": str(e)}, 500

        try:
            email = Helpers.verify_reset_token(token, 3600)
            if email is None:
                Loggger.warn("Cannot verify reset token for user")
                return {"error": "Cannot verify reset token"}, 400

            if not UserService.change_password(email, data.get("password")):
                Loggger.error(f"Failed to reset password for {email}")
                return {"error": f"Failed to reset password for {email}"}, 500
            return {"msg": "Password changed successfully"}, 200
        except Exception as e:
            Loggger.exception(f"Unexpected error {str(e)} occurred")
            return {"generic_error": str(e)}, 500
