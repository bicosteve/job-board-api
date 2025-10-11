from flask_restful import Api

from .controllers.users import UserRegister, UserLogin


def register_routes(app):
    api = Api(app)
    api.add_resource(UserRegister, "/v0/api/profile/register")
    api.add_resource(UserLogin, "/v0/api/profile/login")
