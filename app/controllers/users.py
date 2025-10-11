from flask_restful import Resource, reqparse

from ..services.user_service import UserService

register_parser = reqparse.RequestParser()
register_parser.add_argument("email", required=True, help="Email is required")
register_parser.add_argument("password", required=True, help="Password is required")
register_parser.add_argument(
    "confirm_password", required=True, help="Confirm password is required"
)

login_parser = reqparse.RequestParser()
login_parser.add_argument("email", required=True, help="Email is required")
login_parser.add_argument("password", required=True, help="Password is required")


class UserRegister(Resource):
    def post(self):
        data = register_parser.parse_args()
        try:
            if data["password"] != data["confirm_password"]:
                return {
                    "msg": f"{data['password']} and {data['confirm_password']} must be the same"
                }, 400
            user = UserService.create_user(data["useranme"])

            return user, 201
        except ValueError as e:
            return {"error": str(e)}, 400


class UserLogin(Resource):
    def post(self):
        data = login_parser.parse_args()
        try:
            user = UserService.create_user(data["username"])
            return user, 200
        except ValueError as e:
            return {"error": str(e)}
