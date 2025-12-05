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
    JobsListController,
    JobObjectController,
    ModifyJobObjectController
)
from .controllers.education_controllers import (
    EducationController
)
from .controllers.profile_controllers import (
    ProfileCreateController,
    ProfileGetController
)

from .controllers.application_controllers import (
    ApplicationsListController,
    ApplicationsCreateController,
    UsersJobApplicationsController,
    UsersJobApplicationController,
    ApplicationUpdateController
)


def register_routes(app):
    base = app.config['API_BASE']
    api = Api(app)

    # App Status Check
    api.add_resource(CheckAppHealthController, f"{base}/health/check")

    # User Routes
    api.add_resource(RegisterUserController, f"{base}/user/register")
    api.add_resource(VerifyUserAccountController, f"{base}/user/verify")
    api.add_resource(LoginUserController, f"{base}/user/login")
    api.add_resource(RequestUserPasswordResetController,
                     f"{base}/user/request-reset")
    api.add_resource(ResetUserPasswordController,
                     f"{base}/user/reset-password")
    api.add_resource(UserProfileController, f"{base}/user/me")

    # Education Routes
    api.add_resource(EducationController, f"{base}/education/create")

    # Profile Routes
    api.add_resource(ProfileCreateController, f"{base}/profile/create")
    api.add_resource(ProfileGetController, f"{base}/profile/get")

    # Admin Routes
    api.add_resource(RegisterAdminController, f"{base}/admin/register")
    api.add_resource(LoginAdminController, f"{base}/admin/login")
    api.add_resource(VerifyAdminAccountController, f"{base}/admin/verify")

    api.add_resource(ModifyJobObjectController,
                     f"{base}/admin/jobs/<int:job_id>")

    # Jobs Routes
    api.add_resource(JobsListController, f"{base}/public/jobs")
    api.add_resource(JobObjectController, f"{base}/public/jobs/<int:job_id>")
    api.add_resource(PostJobController, f"{base}/admin/jobs/create")

    # Job Application Routes
    api.add_resource(ApplicationsCreateController,
                     f"{base}/applications/job/create")
    api.add_resource(ApplicationsListController,
                     f"{base}/applications/job/list")
    api.add_resource(UsersJobApplicationsController,
                     f"{base}/applications/user/list")
    api.add_resource(UsersJobApplicationController,
                     f"{base}/applications/job/<int:application_id>")
    api.add_resource(ApplicationUpdateController,
                     f"{base}/applications/job/update/<int:application_id>")
