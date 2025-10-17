from flask import jsonify, make_response
from flask_restful import Resource, request
from marshmallow import ValidationError
from jwt import ExpiredSignatureError, InvalidTokenError


from ..services.user_service import UserService
from ..schemas.user import RegisterSchema, LoginSchema, VerifyAccountSchema
from ..utils.exceptions import (
    InvalidCredentialsError,
    UserExistError,
    GenericDatabaseError,
)
from ..utils.security import Security
from ..utils.helpers import Helpers


register_schema = RegisterSchema()
login_schema = LoginSchema()
verify_account_schema = VerifyAccountSchema()


class UserRegister(Resource):
    def post(self):
        try:
            data = register_schema.load(request.get_json())
        except ValidationError as e:
            return {"error": str(e)}, 400

        email = data["email"]
        password = data["password"]
        username = data["email"].split("@")[0]

        try:
            user = UserService.register_user(username, email, password)
            if user and user["rows_affected"] > 0:
                code = Helpers.generate_verification_code()
                is_stored = UserService.store_verification_code(email, code)
                if is_stored:
                    return {
                        "msg": "user created",
                        "verification_code": code,
                        "email": email,
                    }, 201
                else:
                    return {"msg": "Verification code error"}, 500
        except UserExistError as e:
            return {"user_error": str(e)}, 400
        except GenericDatabaseError as e:
            return {"db_error": str(e)}, 500
        except Exception as e:
            return {"generic_error": str(e)}, 500


class UserLogin(Resource):
    def post(self):
        try:
            data = login_schema.load(request.get_json())
        except ValidationError as e:
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
            return {"error": str(e)}, 500
        except InvalidCredentialsError as e:
            return {"error": str(e)}, 401
        except Exception as e:
            return {"error": str(e)}, 500


class UserProfile(Resource):
    def get(self):
        """Gets user profile and return the details"""
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return {"error": "Authorization missing header"}, 401
        if not auth_header.startswith("Bearer "):
            return {"error": "Invalid authorization header format"}, 401

        token = auth_header.split(" ")[1]

        try:
            payload = Security.decode_jwt_token(token)
            profile_id = payload.get("profile_id")

            if not profile_id:
                return {"error": "Invalid payload"}, 401

            user = UserService.get_user_profile(profile_id)
            if not user:
                return {"error": "User not found"}, 404

            return user, 200

        except ExpiredSignatureError:
            return {"error": "token has expired"}, 401
        except InvalidTokenError:
            return {"error": "Invalid token"}, 401
        except Exception as e:
            return {"error": str(e)}, 500


class UserVerifyAccount(Resource):
    def post(self):
        try:
            data = verify_account_schema.load(request.get_json())
        except ValidationError as e:
            return {"error": str(e)}, 400

        email = data["email"]
        verification_code = data["verification_code"]

        try:
            verified = UserService.verify_account(email, verification_code)
            if verified:
                return {"msg": "user verified successfully"}, 200
            else:
                return {"error": "error while verifying account"}, 500
        except UserExistError as e:
            return {"user_error": str(e)}, 400
        except GenericDatabaseError as e:
            return {"db_error": str(e)}, 500
        except Exception as e:
            return {"generic_error": str(e)}, 500
