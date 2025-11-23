import unittest
from unittest.mock import patch, MagicMock
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
            mock_get_db.side_effect = pymysql.MySQLError(
                "DB connection failed")

            with self.assertRaises(GenericDatabaseError):
                UserRepository.find_user_by_mail(email)

    def test_find_user_by_mail_generic_exception(self):
        """Should raise GenericDatabaseError on unexpected error"""
        email = "error@example.com"

        with patch("app.repositories.user_repository.DB.get_db") as mock_get_db:
            mock_get_db.side_effect = Exception("Something broke")

            with self.assertRaises(GenericDatabaseError):
                UserRepository.find_user_by_mail(email)

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
            self.assertEqual(fake_user["user_id"], 1)

    def test_find_user_by_id_not_found(self):
        """Shoud return None"""
        id = 1

        with patch("app.repositories.user_repository.DB.get_db") as mock_get_db:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()

            mock_cursor.fetchone.return_value = None
            mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
            mock_get_db.return_value = mock_conn

            result = UserRepository.find_user_by_id(id)

            mock_cursor.execute.assert_called_once()
            self.assertIsNone(result)

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
        result = UserRepository.add_user(email, password_hash , 1)

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
