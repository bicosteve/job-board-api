import unittest
from unittest.mock import MagicMock, patch

import pymysql

from app.repositories.user_repository import UserRepository
from app.utils.exceptions import GenericDatabaseError


class TestUserRepository(unittest.TestCase):

    def test_find_user_by_mail_success(self):
        """Should return user object"""
        # Arrange
        fake_user = {
            "user_id": 1,
            "email": "test@example.com",
            "hash": "somehash",
            "status": 1,
            "is_deactivated": 0,
            "created_at": "2025-10-25 00:00:00",
        }

        with patch("app.repositories.user_repository.DB.get_db") as mock_get_db:

            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = fake_user
            mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
            mock_get_db.return_value = mock_conn

            # Act
            result = UserRepository.find_user_by_mail("test@example.com")
            self.assertTrue(isinstance(result, dict))

            # Assert
            mock_cursor.execute.assert_called_once()
            mock_cursor.fetchone.assert_called_once()
            self.assertIsInstance(result, dict)
            self.assertEqual(result["email"], "test@example.com")
            self.assertEqual(result["status"], 1)
            self.assertEqual(result["user_id"], 1)
            self.assertIn("hash", result)

    def test_find_user_by_mail_not_found(self):
        """Should return None if no user is found"""

        # Arrange
        email = "error@example.com"

        with patch("app.repositories.user_repository.DB.get_db") as mock_get_db:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = None
            mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
            mock_get_db.return_value = mock_conn

            # Act
            result = UserRepository.find_user_by_mail(email)

            # Assert
            mock_cursor.execute.assert_called_once()
            self.assertIsNone(result)

    def test_find_user_by_mail_mysql_error(self):
        """Raise GenericDatabaseError on Mysql error"""
        email = "error@example.com"

        with patch("app.repositories.user_repository.DB.get_db") as mock_get_db:
            mock_get_db.side_effect = pymysql.MySQLError("DB connection failed")

            with self.assertRaises(GenericDatabaseError):
                UserRepository.find_user_by_mail(email)

    def test_find_user_by_mail_generic_exception(self):
        """Should raise GenericDatabaseError on unexpected error"""
        email = "error@example.com"

        with patch("app.repositories.user_repository.DB.get_db") as mock_get_db:
            mock_get_db.side_effect = Exception("Something broke")

            with self.assertRaises(GenericDatabaseError):
                UserRepository.find_user_by_mail(email)

    def test_find_user_by_mail_null_is_deactivated_defaults_to_false(self):
        """When the joined setting row is missing, is_deactivated is False."""

        fake_user = {
            "user_id": 1,
            "email": "test@example.com",
            "hash": "somehash",
            "status": 1,
            "is_deactivated": None,
            "created_at": "2025-10-25 00:00:00",
        }

        with patch("app.repositories.user_repository.DB.get_db") as mock_get_db:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = fake_user
            mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
            mock_get_db.return_value = mock_conn

            result = UserRepository.find_user_by_mail("test@example.com")

            self.assertEqual(result["is_deactivated"], False)

    def test_find_user_by_id_success(self):
        """Should return user object if success"""
        user_id = 1
        fake_user = {
            "user_id": user_id,
            "email": "test@example.com",
            "status": 1,
            "reset_token": "some-reset-token",
            "created_at": "2025-10-25 00:00:00",
            "updated_at": "2025-10-25 00:00:00",
        }

        with patch("app.repositories.user_repository.DB.get_db") as mock_get_db:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = fake_user
            mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
            mock_get_db.return_value = mock_conn

            # Act
            result = UserRepository.find_user_by_id(user_id)

            # Assert
            mock_cursor.execute.assert_called_once()
            mock_cursor.fetchone.assert_called_once()
            self.assertIsInstance(result, dict)
            self.assertEqual(result["user_id"], 1)
            self.assertEqual(result["email"], "test@example.com")
            self.assertEqual(result["reset_token"], "some-reset-token")

    def test_find_user_by_id_not_found(self):
        """Should return None"""
        user_id = 1

        with patch("app.repositories.user_repository.DB.get_db") as mock_get_db:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()

            mock_cursor.fetchone.return_value = None
            mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
            mock_get_db.return_value = mock_conn

            result = UserRepository.find_user_by_id(user_id)

            mock_cursor.execute.assert_called_once()
            self.assertIsNone(result)

    def test_find_user_by_id_mysql_error(self):
        """Should raise GenericDatabaseError on pymysql failure."""
        with patch("app.repositories.user_repository.DB.get_db") as mock_get_db:
            mock_get_db.side_effect = pymysql.MySQLError("DB connection failed")

            with self.assertRaises(GenericDatabaseError):
                UserRepository.find_user_by_id(1)

    def test_find_user_by_id_generic_error(self):
        """Should raise GenericDatabaseError on generic failure."""
        with patch("app.repositories.user_repository.DB.get_db") as mock_get_db:
            mock_get_db.side_effect = Exception("Something broke")

            with self.assertRaises(GenericDatabaseError):
                UserRepository.find_user_by_id(1)

    @patch("app.repositories.user_repository.DB.get_db")
    def test_add_user_success(self, mock_get_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__.return_value = mock_cursor
        mock_cursor.rowcount = 1

        mock_conn.cursor.return_value = mock_cursor
        mock_get_db.return_value = mock_conn

        email = "test@example.com"
        password_hash = "hashp"

        # Act
        result = UserRepository.add_user(email, password_hash, 1)

        # Assert
        # Normalize whitespace in the executed SQL
        executed_sql = " ".join(mock_cursor.execute.call_args[0][0].split())
        expected_sql = "INSERT INTO `user`(hash,email,status) VALUES (%s,%s,%s)"
        self.assertEqual(executed_sql, expected_sql)

        # Check parameters
        executed_params = mock_cursor.execute.call_args[0][1]
        expected_params = (password_hash, email, 1)
        self.assertEqual(executed_params, expected_params)

        mock_conn.commit.assert_called_once()
        self.assertEqual(result, 1)

    @patch("app.repositories.user_repository.DB.get_db")
    def test_add_user_fail(self, mock_get_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__.return_value = mock_cursor
        mock_cursor.rowcount = 0

        mock_conn.cursor.return_value = mock_cursor
        mock_get_db.return_value = mock_conn

        result = UserRepository.add_user("duplicate@example.com", "hashp", 1)

        # Assert
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()
        self.assertEqual(result, 0)

    @patch("app.repositories.user_repository.Logger")
    @patch("app.repositories.user_repository.DB.get_db")
    def test_add_user_mysql_error(self, mock_get_db, mock_logger):
        # Arrange
        mock_conn = MagicMock()
        mock_conn.cursor.side_effect = Exception("DB error")
        mock_get_db.return_value = mock_conn

        # Act & assert
        with self.assertRaises(GenericDatabaseError):
            UserRepository.add_user("test@example.com", "hashp", 1)
        mock_logger.error.assert_called()

    @patch("app.repositories.user_repository.Logger")
    @patch("app.repositories.user_repository.DB.get_db")
    def test_add_user_pymysql_error(self, mock_get_db, mock_logger):
        # Arrange
        mock_conn = MagicMock()
        mock_conn.cursor.side_effect = pymysql.MySQLError("MySQL failure")
        mock_get_db.return_value = mock_conn

        # Act & Assert
        with self.assertRaises(GenericDatabaseError):
            UserRepository.add_user("test@example.com", "hashp", 1)
        mock_logger.error.assert_called()

    # ---------------------- update_user_status ----------------------
    def test_update_user_status_success_active(self):
        """Should return rowcount for both updates and use is_deactivated=0 when active."""
        with patch("app.repositories.user_repository.DB.get_db") as mock_get_db:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.__enter__.return_value = mock_cursor
            # First fetchone -> user_id row.
            mock_cursor.fetchone.return_value = {"user_id": 7}
            # Two rowcounts (UPDATE user + INSERT user_setting).
            mock_cursor.rowcount = 1
            mock_conn.cursor.return_value = mock_cursor
            mock_get_db.return_value = mock_conn

            result = UserRepository.update_user_status("test@example.com", 1)

            self.assertEqual(result, 2)
            mock_conn.commit.assert_called_once()
            # Three queries: SELECT user_id, UPDATE user, INSERT user_setting.
            self.assertEqual(mock_cursor.execute.call_count, 3)

    def test_update_user_status_success_deactivated(self):
        """When status != 1, is_deactivated should be 1."""
        with patch("app.repositories.user_repository.DB.get_db") as mock_get_db:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.__enter__.return_value = mock_cursor
            mock_cursor.fetchone.return_value = {"user_id": 7}
            mock_cursor.rowcount = 1
            mock_conn.cursor.return_value = mock_cursor
            mock_get_db.return_value = mock_conn

            UserRepository.update_user_status("test@example.com", 0)

            # The third execute call is the user_setting UPSERT.
            third_call_args = mock_cursor.execute.call_args_list[2]
            self.assertEqual(third_call_args[0][1], (1, 7))

    def test_update_user_status_user_not_found_returns_zero(self):
        """Returns 0 and skips follow-up statements when email not found."""
        with patch("app.repositories.user_repository.DB.get_db") as mock_get_db:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.__enter__.return_value = mock_cursor
            mock_cursor.fetchone.return_value = None
            mock_conn.cursor.return_value = mock_cursor
            mock_get_db.return_value = mock_conn

            result = UserRepository.update_user_status("missing@example.com", 1)

            self.assertEqual(result, 0)
            mock_conn.commit.assert_not_called()

    def test_update_user_status_mysql_error_rolls_back(self):
        with patch("app.repositories.user_repository.DB.get_db") as mock_get_db:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.__enter__.return_value = mock_cursor
            mock_cursor.execute.side_effect = pymysql.MySQLError("boom")
            mock_conn.cursor.return_value = mock_cursor
            mock_get_db.return_value = mock_conn

            with self.assertRaises(GenericDatabaseError):
                UserRepository.update_user_status("test@example.com", 1)

            mock_conn.rollback.assert_called_once()

    def test_update_user_status_generic_error_rolls_back(self):
        with patch("app.repositories.user_repository.DB.get_db") as mock_get_db:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.__enter__.return_value = mock_cursor
            mock_cursor.execute.side_effect = Exception("boom")
            mock_conn.cursor.return_value = mock_cursor
            mock_get_db.return_value = mock_conn

            with self.assertRaises(GenericDatabaseError):
                UserRepository.update_user_status("test@example.com", 1)

            mock_conn.rollback.assert_called_once()

    # ---------------------- store_reset_token ----------------------
    def test_store_reset_token_success(self):
        with patch("app.repositories.user_repository.DB.get_db") as mock_get_db:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.__enter__.return_value = mock_cursor
            mock_cursor.rowcount = 1
            mock_conn.cursor.return_value = mock_cursor
            mock_get_db.return_value = mock_conn

            result = UserRepository.store_reset_token("test@example.com", "token123")

            self.assertEqual(result, 1)
            mock_conn.commit.assert_called_once()
            # Ensure parameters are passed in the right order (token, email).
            params = mock_cursor.execute.call_args[0][1]
            self.assertEqual(params, ("token123", "test@example.com"))

    def test_store_reset_token_returns_zero_when_no_row_updated(self):
        with patch("app.repositories.user_repository.DB.get_db") as mock_get_db:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.__enter__.return_value = mock_cursor
            mock_cursor.rowcount = 0
            mock_conn.cursor.return_value = mock_cursor
            mock_get_db.return_value = mock_conn

            result = UserRepository.store_reset_token("ghost@example.com", "x")

            self.assertEqual(result, 0)

    def test_store_reset_token_mysql_error(self):
        with patch("app.repositories.user_repository.DB.get_db") as mock_get_db:
            mock_conn = MagicMock()
            mock_conn.cursor.side_effect = pymysql.MySQLError("fail")
            mock_get_db.return_value = mock_conn

            with self.assertRaises(GenericDatabaseError):
                UserRepository.store_reset_token("test@example.com", "x")

    def test_store_reset_token_generic_error(self):
        with patch("app.repositories.user_repository.DB.get_db") as mock_get_db:
            mock_conn = MagicMock()
            mock_conn.cursor.side_effect = Exception("fail")
            mock_get_db.return_value = mock_conn

            with self.assertRaises(GenericDatabaseError):
                UserRepository.store_reset_token("test@example.com", "x")

    # ---------------------- get_reset_token ----------------------
    def test_get_reset_token_success(self):
        fake_row = {
            "reset_token": "abc-token",
            "updated_at": "2025-01-01 12:00:00",
        }
        with patch("app.repositories.user_repository.DB.get_db") as mock_get_db:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.__enter__.return_value = mock_cursor
            mock_cursor.fetchone.return_value = fake_row
            mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
            mock_get_db.return_value = mock_conn

            result = UserRepository.get_reset_token("test@example.com")

            self.assertEqual(
                result,
                {
                    "reset-token": "abc-token",
                    "time": "2025-01-01 12:00:00",
                },
            )

    def test_get_reset_token_not_found(self):
        with patch("app.repositories.user_repository.DB.get_db") as mock_get_db:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.__enter__.return_value = mock_cursor
            mock_cursor.fetchone.return_value = None
            mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
            mock_get_db.return_value = mock_conn

            result = UserRepository.get_reset_token("ghost@example.com")

            self.assertIsNone(result)

    def test_get_reset_token_mysql_error(self):
        with patch("app.repositories.user_repository.DB.get_db") as mock_get_db:
            mock_get_db.side_effect = pymysql.MySQLError("fail")

            with self.assertRaises(GenericDatabaseError):
                UserRepository.get_reset_token("test@example.com")

    def test_get_reset_token_generic_error(self):
        with patch("app.repositories.user_repository.DB.get_db") as mock_get_db:
            mock_get_db.side_effect = Exception("fail")

            with self.assertRaises(GenericDatabaseError):
                UserRepository.get_reset_token("test@example.com")

    # ---------------------- update_password ----------------------
    def test_update_password_success(self):
        with patch("app.repositories.user_repository.DB.get_db") as mock_get_db:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.__enter__.return_value = mock_cursor
            mock_cursor.rowcount = 1
            mock_conn.cursor.return_value = mock_cursor
            mock_get_db.return_value = mock_conn

            result = UserRepository.update_password("test@example.com", "newhash")

            self.assertEqual(result, 1)
            mock_conn.commit.assert_called_once()
            params = mock_cursor.execute.call_args[0][1]
            self.assertEqual(params, ("newhash", "test@example.com"))

    def test_update_password_returns_zero_when_no_row_updated(self):
        with patch("app.repositories.user_repository.DB.get_db") as mock_get_db:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.__enter__.return_value = mock_cursor
            mock_cursor.rowcount = 0
            mock_conn.cursor.return_value = mock_cursor
            mock_get_db.return_value = mock_conn

            result = UserRepository.update_password("ghost@example.com", "h")

            self.assertEqual(result, 0)

    def test_update_password_mysql_error(self):
        with patch("app.repositories.user_repository.DB.get_db") as mock_get_db:
            mock_conn = MagicMock()
            mock_conn.cursor.side_effect = pymysql.MySQLError("fail")
            mock_get_db.return_value = mock_conn

            with self.assertRaises(GenericDatabaseError):
                UserRepository.update_password("test@example.com", "h")

    def test_update_password_generic_error(self):
        with patch("app.repositories.user_repository.DB.get_db") as mock_get_db:
            mock_conn = MagicMock()
            mock_conn.cursor.side_effect = Exception("fail")
            mock_get_db.return_value = mock_conn

            with self.assertRaises(GenericDatabaseError):
                UserRepository.update_password("test@example.com", "h")


if __name__ == "__main__":
    unittest.main()
