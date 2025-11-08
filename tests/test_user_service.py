import unittest
from unittest.mock import patch
from datetime import datetime

from app.services.user_service import UserService
from app.utils.exceptions import (
    GenericDatabaseError,
    InvalidCredentialsError,
    InvalidLoginAttemptError,
    UserExistError,
)


class TestUserService(unittest.TestCase):
    def setUp(self):
        self.user_id = 1
        self.email = "test@example.com"
        self.hash = "hashedpass"
        self.status = 1
        self.is_deactivated = 0
        self.password = "mypassword"
        self.created_at = "2025-01-01 12:00:00"
        self.code = "123456"

    @patch("app.services.user_service.UserRepository.find_user_by_id")
    def test_get_user_profile_returns_user_dict(self, mock_user_repo):
        fake_user = {
            "user_id": self.user_id,
            "email": self.email,
            "status": 1,
            "reset_token": "reset12345",
            "created_at": self.created_at,
            "modified_at": "2025-01-01 12:00:00",
        }

        mock_user_repo.return_value = fake_user

        result = UserService.get_user_profile(1)

        expected_keys = [
            "user_id",
            "email",
            "status",
            "reset_token",
            "created_at",
            "updated_at",
        ]

        self.assertEqual(result["email"], fake_user["email"])
        self.assertListEqual(sorted(result.keys()), sorted(expected_keys))
        mock_user_repo.assert_called_once_with(1)

    @patch("app.services.user_service.UserRepository.find_user_by_id")
    def test_get_user_profile_raises_error_when_user_not_found(self, mock_user_repo):
        # Arrange
        mock_user_repo.return_value = None

        # Act & Assert
        with self.assertRaises(GenericDatabaseError) as context:
            UserService.get_user_profile(999)

        self.assertIn("error occurred while finding user", str(context.exception))
        mock_user_repo.assert_called_once_with(999)

    @patch("app.services.user_service.Security.check_password", return_value=True)
    @patch("app.services.user_service.UserRepository.find_user_by_mail")
    def test_get_user_returns_user_success(self, mock_user_repo, mock_check_password):
        """User exists, verified, and password matches"""
        user_data = {
            "user_id": self.user_id,
            "email": self.email,
            "hash": self.hash,
            "status": self.status,
            "created_at": self.created_at,
        }

        mock_user_repo.return_value = user_data

        user = UserService.get_user(self.email, self.password)

        self.assertEqual(user["email"], self.email)
        mock_user_repo.assert_called_once_with(self.email)
        mock_check_password.assert_called_once_with(self.password, "hashedpass")

    @patch("app.services.user_service.Loggger.warn")
    @patch(
        "app.services.user_service.UserRepository.find_user_by_mail", return_value=None
    )
    def test_get_user_not_found(self, mock_find_user, mock_warn):
        """User not found"""

        mock_find_user.return_value = None

        with self.assertRaises(InvalidCredentialsError) as context:
            UserService.get_user(self.email, self.password)

        self.assertIn("Invalid email", str(context.exception))
        mock_warn.assert_called_once_with(f"user not found for email {self.email}")

    @patch("app.services.user_service.Loggger.warn")
    @patch("app.services.user_service.UserRepository.find_user_by_mail")
    def test_get_user_not_verified(self, mock_user, mock_warn):
        user_data = {
            "user_id": self.user_id,
            "email": self.email,
            "hash": self.hash,
            "status": self.status,
            "is_deactivated": self.is_deactivated,
            "created_at": self.created_at,
        }

        mock_user.return_value = {**user_data, "status": 0}

        with self.assertRaises(InvalidLoginAttemptError) as ctx:
            UserService.get_user(self.email, self.password)

        self.assertIn("not verified", str(ctx.exception))
        mock_warn.assert_called_once_with(f"user not verified for {self.email}")

    @patch("app.services.user_service.Loggger.warn")
    @patch("app.services.user_service.Security.check_password", return_value=False)
    @patch("app.services.user_service.UserRepository.find_user_by_mail")
    def test_get_user_invalid_password(
        self, mock_find_user, mock_check_password, mock_warn
    ):
        user_data = {
            "user_id": self.user_id,
            "email": self.email,
            "hash": self.hash,
            "status": self.status,
            "is_deactivated": self.is_deactivated,
            "created_at": self.created_at,
        }

        mock_find_user.return_value = user_data

        with self.assertRaises(InvalidCredentialsError) as ctx:
            UserService.get_user(self.email, "wrongpass")

        self.assertIn("Invalid email or password", str(ctx.exception))
        mock_warn.assert_called_once_with(f"Invalid password for user {self.email}")
        mock_check_password.assert_called_once_with("wrongpass", "hashedpass")

    @patch("app.services.user_service.Loggger.warn")
    @patch("app.services.user_service.Security.hash_password")
    @patch("app.services.user_service.UserRepository.find_user_by_mail")
    @patch("app.services.user_service.UserRepository.add_user")
    def test_register_user_success(
        self, mock_add_user, mock_find_user, mock_hash_password, mock_warn
    ):

        # Arrange
        mock_find_user.return_value = None
        mock_hash_password.return_value = "hashed_pass"
        mock_add_user.return_value = 1

        # Act
        result = UserService.register_user("Doe", self.email, self.password)

        # Assert
        mock_find_user.assert_called_once_with(self.email)
        mock_hash_password.assert_called_once_with(self.password)
        mock_add_user.assert_called_once_with(self.email, "hashed_pass", 0)
        mock_warn.assert_not_called()
        self.assertEqual(result, {"rows_affected": 1})

    @patch("app.services.user_service.Loggger.warn")
    @patch("app.services.user_service.UserRepository.find_user_by_mail")
    def test_register_user_already_exist(self, mock_find_user, mock_warn):
        """Test register user already existing"""
        mock_find_user.return_value = {"email": self.email}

        with self.assertRaises(UserExistError):
            UserService.register_user("Doe", self.email, self.password)

        mock_warn.assert_called_once_with(f"User already exist for email {self.email}")

    @patch("app.services.user_service.UserCache.store_verification_code")
    def test_store_user_verification_code(self, mock_store_code):
        """Should return True when code is successfully stored in cache"""
        # Arrange
        mock_store_code.return_value = True

        # Act
        result = UserService.store_verification_code(self.email, self.code)

        # Assert
        mock_store_code.assert_called_once_with(self.email, self.code)
        self.assertIs(result, True)

    @patch("app.services.user_service.UserCache.store_verification_code")
    def test_store_user_verification_code_returns_false(self, mock_store_code):
        """Should return False if verification code is not stored in cache"""

        # Arrange
        mock_store_code.return_value = False

        # Act
        result = UserService.store_verification_code(self.email, self.code)

        # Assert
        mock_store_code.assert_called_once_with(self.email, self.code)
        self.assertIs(result, False)

    @patch(
        "app.services.user_service.UserRepository.update_user_status", return_value=1
    )
    @patch("app.services.user_service.UserCache.verify_code", return_value=True)
    def test_verify_account_cache_match(self, mock_verify_code, mock_update_status):
        """Should return True when verification code is valid"""
        mock_verify_code.return_value = True

        result = UserService.verify_account(self.email, self.code)

        mock_verify_code.assert_called_once_with(self.email, self.code)
        mock_update_status.assert_not_called()
        self.assertTrue(result)

    @patch(
        "app.services.user_service.UserRepository.update_user_status", return_value=1
    )
    @patch("app.services.user_service.UserCache.verify_code", return_value=False)
    def test_verify_account_success_with_db_update(
        self, mock_verify_code, mock_update_status
    ):
        """Should return True when cache fails but DB update succeeds"""
        mock_verify_code.return_value = False
        mock_update_status.return_value = 1

        result = UserService.verify_account(self.email, self.code)

        mock_verify_code.assert_called_once_with(self.email, self.code)
        mock_update_status.assert_called_once_with(self.email)
        self.assertTrue(result)

    @patch(
        "app.services.user_service.UserRepository.update_user_status", return_value=0
    )
    @patch("app.services.user_service.UserCache.verify_code", return_value=False)
    def test_verify_account_db_update_fails(self, mock_verify_code, mock_update_status):
        """Should return False if DB update affects no rows"""
        mock_verify_code.return_value = False
        mock_update_status.return_value = 0

        result = UserService.verify_account(self.email, self.code)

        mock_verify_code.assert_called_once_with(self.email, self.code)
        mock_update_status.assert_called_once_with(self.email)
        self.assertFalse(result)

    @patch("app.services.user_service.Loggger.exception")
    @patch("app.services.user_service.UserCache.verify_code")
    def test_verify_account_raises_generic_db_error(
        self, mock_verify_code, mock_logger
    ):
        """Should raise GenericDatabaseError when an exception occurs"""
        mock_verify_code.side_effect = Exception("DB connection failed")

        with self.assertRaises(GenericDatabaseError):
            UserService.verify_account(self.email, self.code)

        mock_verify_code.assert_called_once_with(self.email, self.code)
        mock_logger.assert_called_once()

    @patch("app.services.user_service.Helpers.generate_reset_token")
    @patch("app.services.user_service.UserCache.hold_reset_token", return_value=True)
    @patch("app.services.user_service.UserRepository.store_reset_token", return_value=1)
    def test_store_reset_token_success(
        self, mock_repository, mock_user_cache, mock_generate_reset_token
    ):
        """Should return a user object if success"""
        token = "sometoken"
        data = {"token": token, "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

        # Arrange
        mock_generate_reset_token.return_value = token
        mock_user_cache.return_value = True
        mock_repository.return_value = 1

        # Act
        result = UserService.store_reset_token(self.email)

        # Assert
        mock_generate_reset_token.assert_called_once_with(self.email)
        mock_user_cache.assert_called_once_with(self.email, data)
        mock_repository.assert_called_once_with(self.email, token)
        self.assertTrue(result)

    def test_get_reset_token_success(self):
        """Should return True if token is returned"""
        token = "sometoken"

        with patch(
            "app.services.user_service.Helpers.compare_token_time"
        ) as mock_compare, patch(
            "app.services.user_service.UserRepository.get_reset_token"
        ) as mock_repo, patch(
            "app.services.user_service.UserCache.retrieve_reset_token"
        ) as mock_cache:
            # Arrange
            mock_cache.return_value = token

            # Act
            result = UserService.get_reset_token(self.email, token)

            # Assert
            mock_cache.assert_called_once_with(self.email, token)
            mock_repo.assert_not_called()
            mock_compare.assert_not_called()
            self.assertEqual(result, token)

    def test_get_reset_token_miss(self):
        """Should return True if token is returned"""
        token = "sometoken"
        data = {
            "reset-token": token,
            "time": str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        }

        with patch(
            "app.services.user_service.Helpers.compare_token_time"
        ) as mock_compare, patch(
            "app.services.user_service.UserRepository.get_reset_token"
        ) as mock_repo, patch(
            "app.services.user_service.UserCache.retrieve_reset_token"
        ) as mock_cache:
            # Arrange
            mock_cache.return_value = None
            mock_repo.return_value = data
            mock_compare.return_value = True

            # Act
            result = UserService.get_reset_token(self.email, token)

            # Assert
            mock_cache.assert_called_once_with(self.email, token)
            mock_repo.assert_called_once_with(self.email)
            mock_compare.assert_called_once_with(data)
            self.assertEqual(result, token)

    def test_change_password_success(self):
        password_hash = "somehash"

        with patch(
            "app.services.user_service.Security.hash_password"
        ) as mock_security, patch(
            "app.services.user_service.UserRepository.update_password"
        ) as mock_repo:

            mock_security.return_value = password_hash
            mock_repo.return_value = 1

            result = UserService.change_password(self.email, self.password)

            # assert
            mock_security.assert_called_once_with(self.password)
            mock_repo.assert_called_once_with(self.email, password_hash)
            self.assertEqual(result, 1)
