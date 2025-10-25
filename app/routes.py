from flask_restful import Api

from .controllers.user_controllers import (
    UserRegister,
    UserLogin,
    UserProfile,
    UserVerifyAccount,
    ResetPasswordRequest,
    AccountPasswordReset
)


def register_routes(app):
    api = Api(app)
    api.add_resource(UserRegister, "/v0/api/profile/register")
    api.add_resource(UserVerifyAccount, "/v0/api/profile/verify")
    api.add_resource(UserLogin, "/v0/api/profile/login")
    api.add_resource(UserProfile, "/v0/api/profile/me")
    api.add_resource(ResetPasswordRequest, "/v0/api/profile/request-reset")
    api.add_resource(AccountPasswordReset, "/v0/api/profile/reset-password")
