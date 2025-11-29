import os


from flask_restful import Api

from .controllers.user_controllers import (
    RegisterUserController,
    LoginUserController,
    UserProfileController,
    VerifyUserAccountController,
    RequestUserPasswordResetController,
    ResetUserPasswordController,
    CheckAppHealthController
)
from .controllers.admin_controllers import (
    RegisterAdminController,
    LoginAdminController,
    VerifyAdminAccountController
)
from .controllers.job_controllers import (
    PostJobController,
    JobsListController
)


def register_routes(app):
    base = app.config['API_BASE']
    api = Api(app)

    # User Routes
    api.add_resource(CheckAppHealthController, f"{base}/health/check")
    api.add_resource(RegisterUserController, f"{base}/profile/register")
    api.add_resource(VerifyUserAccountController, f"{base}/profile/verify")
    api.add_resource(LoginUserController, f"{base}/profile/login")
    api.add_resource(UserProfileController, f"{base}/profile/me")
    api.add_resource(RequestUserPasswordResetController,
                     f"{base}/profile/request-reset")
    api.add_resource(ResetUserPasswordController,
                     f"{base}/profile/reset-password")

    # Admin Routes
    api.add_resource(RegisterAdminController, f"{base}/admin/register")
    api.add_resource(LoginAdminController, f"{base}/admin/login")
    api.add_resource(VerifyAdminAccountController, f"{base}/admin/verify")
    api.add_resource(PostJobController, f"{base}/admin/jobs")

    # Public Routes
    api.add_resource(JobsListController, f"{base}/public/jobs")
    # api.add_resource(JobsListController, f"{base}/public/jobs/{1}")
