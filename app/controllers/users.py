from flask import jsonify, make_response
from flask_restful import Resource, request
from marshmallow import ValidationError
from jwt import ExpiredSignatureError, InvalidTokenError


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

    def post(self):
        try:
            data = UserRegister.register_schema.load(request.get_json())
        except ValidationError as e:
            Loggger.exception(str(e))
            return {"error": str(e)}, 400

        email = data["email"]
        password = data["password"]
        username = data["email"].split("@")[0]

        try:
            user = UserService.register_user(username, email, password)
            if user and user["rows_affected"] > 0:
                code = Helpers.generate_verification_code()
                if UserService.store_verification_code(email, code):
                    return {
                        "msg": "user created",
                        "verification_code": code,
                        "email": email,
                    }, 201
                else:
                    return {"msg": "Verification code error"}, 500
        except UserExistError as e:
            Loggger.exception(str(e))
            return {"user_error": str(e)}, 400
        except GenericDatabaseError as e:
            Loggger.exception(str(e))
            return {"db_error": str(e)}, 500
        except Exception as e:
            Loggger.exception(str(e))
            return {"generic_error": str(e)}, 500


class UserLogin(Resource):
    login_schema = LoginSchema()

    def post(self):
        try:
            data = UserLogin.login_schema.load(request.get_json())
        except ValidationError as e:
            Loggger.exception(str(e))
            return {"error": str(e)}, 400

        email = data["email"]
        password = data["password"]

        try:
            user = UserService.get_user(email, password)
            token = Security.create_jwt_token(
                user["profile_id"], user["email"])
            response = make_response(
                jsonify(
                    {
                        "msg": "Login success",
                        "token": token,
                    }
                ),
                200,
            )
            response.headers["Authorization"] = f"Bearer {token}"
            return response
        except GenericDatabaseError as e:
            Loggger.exception(str(e))
            return {"error": str(e)}, 500
        except InvalidCredentialsError as e:
            Loggger.exception(str(e))
            return {"error": str(e)}, 401
        except Exception as e:
            Loggger.exception(str(e))
            return {"error": str(e)}, 500


class UserProfile(Resource):
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
            profile_id = payload.get("profile_id")

            if not profile_id:
                return {"error": "Invalid payload"}, 401

            user = UserService.get_user_profile(profile_id)
            if not user:
                Loggger.warn(f"User with profile {profile_id}")
                return {"error": "User not found"}, 404

            return user, 200

        except ExpiredSignatureError as e:
            Loggger.exception(str(e))
            return {"error": "token has expired"}, 401
        except InvalidTokenError as e:
            Loggger.exception(str(e))
            return {"error": "Invalid token"}, 401
        except Exception as e:
            Loggger.exception(str(e))
            return {"error": str(e)}, 500


class UserVerifyAccount(Resource):
    verify_account_schema = VerifyAccountSchema()

    def post(self):
        try:
            data = UserVerifyAccount.verify_account_schema.load(
                request.get_json())
        except ValidationError as e:
            Loggger.exception(str(e))
            return {"error": str(e)}, 400

        email = data["email"]
        verification_code = data["verification_code"]

        try:
            is_verified = UserService.verify_account(email, verification_code)
            if not is_verified:
                return {"error": "error while verifying account"}, 500
            return {"error": "account verification success"}, 200
        except UserExistError as e:
            Loggger.exception(str(e))
            return {"user_error": str(e)}, 400
        except GenericDatabaseError as e:
            Loggger.exception(str(e))
            return {"db_error": str(e)}, 500
        except Exception as e:
            Loggger.exception(str(e))
            return {"generic_error": str(e)}, 500


class ResetPasswordRequest(Resource):
    request_reset_password_schema = RequestResetPasswordSchema()

    def post(self):
        try:
            data = ResetPasswordRequest.request_reset_password_schema.load(
                request.get_json())
        except ValidationError as e:
            Loggger.exception(str(e))
            return {'error': str(e)}, 400

        try:
            email = data['email']
            token_data = UserService.store_reset_token(email)
            if not token_data:
                Loggger.warn('An error occurred while storing reset token')
                return {'error':
                        'An error occurred while storing reset token'}, 500
            return {'data': token_data}, 201
        except Exception as e:
            Loggger.exception(str(e))
            return {'generic_error': str(e)}, 500


class AccountPasswordReset(Resource):
    reset_password_schema = ResetPasswordSchema()

    def post(self):
        token = request.args.get('token')
        if len(token) < 1:
            Loggger.warn('No reset token provided in the request')
            return {'error': 'Token is required'}

        try:
            data = AccountPasswordReset.reset_password_schema.load(
                request.get_json())

        except Exception as e:
            Loggger.exception(str(e))
            return {'generic_error': str(e)}, 500

        try:
            email = Helpers.verify_reset_token(token, 3600)
            if email is None:
                Loggger.warn('Cannot verify reset token for user')
                return {'error': 'Cannot verify reset token'}, 400

            if not UserService.change_password(email, data.get('password')):
                Loggger.error(f'Failed to reset password for {email}')
                return {'error': f'Failed to reset password for {email}'}, 500
            return {'msg': 'Password changed successfully'}, 200
        except Exception as e:
            Loggger.exception(str(e))
            return str(e)
