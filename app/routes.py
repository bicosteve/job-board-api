from flask_restful import Api

from .controllers.users import UserListResource


def register_routes(app):
    api = Api(app)
    api.add_resource(UserListResource, "/v0/api/users")
