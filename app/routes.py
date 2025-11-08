import os

from dotenv import load_dotenv
from flask_restful import Api

from .controllers.user_controllers import (
    UserRegister,
    UserLogin,
    UserProfile,
    UserVerifyAccount,
    ResetPasswordRequest,
    AccountPasswordReset,
    AppHealthCheck
)

load_dotenv()


def register_routes(app):
    API_V = app.config['API_BASE']
    # API_V = os.getenv('API_V', '/v0/api')
    api = Api(app)

    api.add_resource(AppHealthCheck, API_V + "/health/check")
    api.add_resource(UserRegister, API_V + "/profile/register")
    api.add_resource(UserVerifyAccount, API_V + "/profile/verify")
    api.add_resource(UserLogin, API_V + "/profile/login")
    api.add_resource(UserProfile, API_V + "/profile/me")
    api.add_resource(ResetPasswordRequest, API_V + "/profile/request-reset")
    api.add_resource(AccountPasswordReset, API_V + "/profile/reset-password")
