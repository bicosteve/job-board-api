from flask_restful import Resource, reqparse

from ..services.user_service import UserService

parser = reqparse.RequestParser()
parser.add_argument("username", required=True, help="Username is required")
parser.add_argument("email", required=True, help="Email is required")
parser.add_argument("password", required=True, help="Password is required")
parser.add_argument(
    "confirm_password", required=True, help="Confirm password is required"
)


class UserListResource(Resource):
    def get(self):
        users = UserService.get_user()

    def post(self):
        data = parser.parse_args()
        try:
            user = UserService.create_user(data["useranme"])
            return user, 201
        except ValueError as e:
            return {"error": str(e)}, 400
