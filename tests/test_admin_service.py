import unittest
from unittest.mock import patch, MagicMock
from app.services.admin_service import AdminService
from app.utils.exceptions import (
    InvalidCredentialsError,
    UserExistError,
    GenericDatabaseError,
    InvalidLoginAttemptError,
    UserDoesNotExistError,
    GenericRedisError,
)


class TestAdminService(unittest.TestCase):
    def setUp(self):
        self.email = "admin@example.com"
        self.password = "secret"
        self.admin = {
            "id": 1,
            "email": self.email,
            "username": "admin",
            "password_hash": "hashedpw",
            "is_deactivated": 1,
        }

    # --- get_admin_profile ---
    @patch("app.services.admin_service.AdminRepository.find_admin_by_id")
    def test_get_admin_profile_success(self, mock_find):
        mock_find.return_value = self.admin
        result = AdminService.get_admin_profile(1)
        self.assertEqual(result["email"], self.email)

    @patch("app.services.admin_service.AdminRepository.find_admin_by_id", return_value=None)
    def test_get_admin_profile_none(self, mock_find):
        result = AdminService.get_admin_profile(1)
        self.assertIsNone(result)

    # --- get_admin_user ---
    @patch("app.services.admin_service.Security.create_jwt_token", return_value="jwt-token")
    @patch("app.services.admin_service.Security.check_password", return_value=True)
    @patch("app.services.admin_service.AdminRepository.find_admin_by_email")
    def test_get_admin_user_success(self, mock_find, mock_check, mock_token):
        mock_find.return_value = self.admin
        result = AdminService.get_admin_user(self.email, self.password)
        self.assertEqual(result["token"], "jwt-token")

    @patch("app.services.admin_service.AdminRepository.find_admin_by_email", return_value=None)
    def test_get_admin_user_not_found(self, mock_find):
        with self.assertRaises(UserDoesNotExistError):
            AdminService.get_admin_user(self.email, self.password)

    @patch("app.services.admin_service.Security.check_password", return_value=False)
    @patch("app.services.admin_service.AdminRepository.find_admin_by_email")
    def test_get_admin_user_invalid_password(self, mock_find, mock_check):
        mock_find.return_value = self.admin
        with self.assertRaises(InvalidCredentialsError):
            AdminService.get_admin_user(self.email, self.password)

    @patch("app.services.admin_service.Security.check_password", return_value=True)
    @patch("app.services.admin_service.AdminRepository.find_admin_by_email")
    def test_get_admin_user_inactive(self, mock_find, mock_check):
        inactive_admin = dict(self.admin)
        inactive_admin["is_deactivated"] = 0
        mock_find.return_value = inactive_admin
        with self.assertRaises(InvalidLoginAttemptError):
            AdminService.get_admin_user(self.email, self.password)

    # --- add_admin_user ---
    @patch("app.services.admin_service.AdminRepository.add_admin", return_value=1)
    @patch("app.services.admin_service.BaseCache.store_verification_code", return_value=True)
    @patch("app.services.admin_service.Security.hash_password", return_value="hashedpw")
    @patch("app.services.admin_service.AdminRepository.find_admin_by_email", return_value=None)
    def test_add_admin_user_success(self, mock_find, mock_hash, mock_store, mock_add):
        data = {"email": self.email, "password": self.password,
                "verification_code": "123456"}
        result = AdminService.add_admin_user(data)
        self.assertEqual(result["rows"], 1)

    @patch("app.services.admin_service.AdminRepository.find_admin_by_email", return_value={"id": 1})
    def test_add_admin_user_exists(self, mock_find):
        data = {"email": self.email, "password": self.password,
                "verification_code": "123456"}
        with self.assertRaises(UserExistError):
            AdminService.add_admin_user(data)

    @patch("app.services.admin_service.BaseCache.store_verification_code", return_value=False)
    @patch("app.services.admin_service.Security.hash_password", return_value="hashedpw")
    @patch("app.services.admin_service.AdminRepository.find_admin_by_email", return_value=None)
    def test_add_admin_user_redis_fail(self, mock_find, mock_hash, mock_store):
        data = {"email": self.email, "password": self.password,
                "verification_code": "123456"}
        with self.assertRaises(GenericRedisError):
            AdminService.add_admin_user(data)

    @patch("app.services.admin_service.AdminRepository.add_admin", return_value=None)
    @patch("app.services.admin_service.BaseCache.store_verification_code", return_value=True)
    @patch("app.services.admin_service.Security.hash_password", return_value="hashedpw")
    @patch("app.services.admin_service.AdminRepository.find_admin_by_email", return_value=None)
    def test_add_admin_user_repo_none(self, mock_find, mock_hash, mock_store, mock_add):
        data = {"email": self.email, "password": self.password,
                "verification_code": "123456"}
        result = AdminService.add_admin_user(data)
        self.assertIsNone(result)

    @patch("app.services.admin_service.AdminRepository.add_admin", return_value=0)
    @patch("app.services.admin_service.BaseCache.store_verification_code", return_value=True)
    @patch("app.services.admin_service.Security.hash_password", return_value="hashedpw")
    @patch("app.services.admin_service.AdminRepository.find_admin_by_email", return_value=None)
    def test_add_admin_user_repo_error(self, mock_find, mock_hash, mock_store, mock_add):
        data = {"email": self.email, "password": self.password,
                "verification_code": "123456"}
        with self.assertRaises(GenericDatabaseError):
            AdminService.add_admin_user(data)

    # --- verify_admin_user ---
    @patch("app.services.admin_service.AdminRepository.update_admin_status", return_value=1)
    @patch("app.services.admin_service.BaseCache.verify_code", return_value=True)
    def test_verify_admin_user_success(self, mock_verify, mock_update):
        data = {"email": self.email, "active_status": 1,
                "verification_code": "123456"}
        result = AdminService.verify_admin_user(data)
        self.assertEqual(result["res"], 1)

    @patch("app.services.admin_service.BaseCache.verify_code", return_value=False)
    def test_verify_admin_user_no_code(self, mock_verify):
        data = {"email": self.email, "active_status": 1,
                "verification_code": "123456"}
        result = AdminService.verify_admin_user(data)
        self.assertIsNone(result)

    @patch("app.services.admin_service.AdminRepository.update_admin_status", return_value=None)
    @patch("app.services.admin_service.BaseCache.verify_code", return_value=True)
    def test_verify_admin_user_repo_none(self, mock_verify, mock_update):
        data = {"email": self.email, "active_status": 1,
                "verification_code": "123456"}
        result = AdminService.verify_admin_user(data)
        self.assertIsNone(result)

    @patch("app.services.admin_service.AdminRepository.update_admin_status", return_value=0)
    @patch("app.services.admin_service.BaseCache.verify_code", return_value=True)
    def test_verify_admin_user_repo_error(self, mock_verify, mock_update):
        data = {"email": self.email, "active_status": 1,
                "verification_code": "123456"}
        with self.assertRaises(GenericDatabaseError):
            AdminService.verify_admin_user(data)

    # --- deactivate_admin_user ---
    @patch("app.services.admin_service.AdminRepository.update_admin_status", return_value=1)
    def test_deactivate_admin_user_success(self, mock_update):
        data = {"email": self.email, "active_status": 0}
        result = AdminService.deactivate_admin_user(data)
        self.assertEqual(result["res"], 1)

    @patch("app.services.admin_service.AdminRepository.update_admin_status", return_value=None)
    def test_deactivate_admin_user_none(self, mock_update):
        data = {"email": self.email, "active_status": 0}
        result = AdminService.deactivate_admin_user(data)
        self.assertIsNone(result)

    @patch("app.services.admin_service.AdminRepository.update_admin_status", return_value=0)
    def test_deactivate_admin_user_error(self, mock_update):
        data = {"email": self.email, "active_status": 0}
        with self.assertRaises(GenericDatabaseError):
            AdminService.deactivate_admin_user(data)

    # --- store_verification_code ---
    @patch("app.services.admin_service.BaseCache.store_verification_code", return_value=True)
    def test_store_verification_code_success(self, mock_store):
        data = {"email": self.email, "code": "123456"}
        result = AdminService.store_verification_code(data)
        self.assertTrue(result)

    @patch("app.services.admin_service.BaseCache.store_verification_code", side_effect=GenericRedisError("fail"))
    def test_store_verification_code_error(self, mock_store):
        data = {"email": self.email, "code": "123456"}
        with self.assertRaises(GenericRedisError):
            AdminService.store_verification_code(data)


if __name__ == "__main__":
    unittest.main()
