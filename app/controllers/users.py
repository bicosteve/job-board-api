from flask import jsonify
from flask_restful import Resource, request
from marshmallow import ValidationError


from ..services.user_service import UserService
from ..schemas.user import RegisterSchema, LoginSchema
from ..utils.exceptions import (
    InvalidCredentialsError,
    UserExistError,
    GenericDatabaseError,
)

register_schema = RegisterSchema()
login_schema = LoginSchema()


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
                return {"msg": "user created"}, 201
        except GenericDatabaseError as e:
            return {"error": str(e)}, 500
        except UserExistError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            return {"error": str(e)}, 500


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
            return {"user": user}, 200
        except GenericDatabaseError as e:
            return {"error": str(e)}, 500
        except InvalidCredentialsError as e:
            return {"error": str(e)}, 401
        except Exception as e:
            return {"error": str(e)}, 500


class UserProfile(Resource):
    pass
