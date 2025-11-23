import unittest
from unittest.mock import patch, MagicMock
import pymysql
from app.repositories.admin_repository import AdminRepository
from app.utils.exceptions import GenericDatabaseError


class TestAdminRepository(unittest.TestCase):
    def setUp(self):
        self.email = "admin@example.com"
        self.admin_id = 1
        self.admin_row = {
            "admin_id": self.admin_id,
            "email": self.email,
            "username": "adminuser",
            "hash": "hashedpw",
            "created_at": "2025-01-01 12:00:00",
            "updated_at": "2025-01-02 12:00:00",
            "is_deactivated": 0,
        }

    # --- find_admin_by_email ---
    @patch("app.repositories.admin_repository.DB.get_db")
    def test_find_admin_by_email_success(self, mock_get_db):
        conn = MagicMock()
        cursor = MagicMock()
        cursor.fetchone.return_value = self.admin_row
        conn.cursor.return_value.__enter__.return_value = cursor
        mock_get_db.return_value = conn

        result = AdminRepository.find_admin_by_email(self.email)

        cursor.execute.assert_called_once()
        self.assertEqual(result["id"], self.admin_id)
        self.assertEqual(result["email"], self.email)
        self.assertFalse(result["is_deactivated"])  # 0 → False

    @patch("app.repositories.admin_repository.DB.get_db")
    def test_find_admin_by_email_not_found(self, mock_get_db):
        conn = MagicMock()
        cursor = MagicMock()
        cursor.fetchone.return_value = None
        conn.cursor.return_value.__enter__.return_value = cursor
        mock_get_db.return_value = conn

        result = AdminRepository.find_admin_by_email(self.email)
        self.assertIsNone(result)

    @patch("app.repositories.admin_repository.DB.get_db", side_effect=Exception("DB fail"))
    def test_find_admin_by_email_error(self, mock_get_db):
        with self.assertRaises(GenericDatabaseError):
            AdminRepository.find_admin_by_email(self.email)

    # --- find_admin_by_id ---
    @patch("app.repositories.admin_repository.DB.get_db")
    def test_find_admin_by_id_success(self, mock_get_db):
        conn = MagicMock()
        cursor = MagicMock()
        cursor.fetchone.return_value = self.admin_row
        conn.cursor.return_value.__enter__.return_value = cursor
        mock_get_db.return_value = conn

        result = AdminRepository.find_admin_by_id(self.admin_id)

        cursor.execute.assert_called_once()
        self.assertEqual(result["id"], self.admin_id)
        self.assertEqual(result["username"], "adminuser")

    @patch("app.repositories.admin_repository.DB.get_db")
    def test_find_admin_by_id_not_found(self, mock_get_db):
        conn = MagicMock()
        cursor = MagicMock()
        cursor.fetchone.return_value = None
        conn.cursor.return_value.__enter__.return_value = cursor
        mock_get_db.return_value = conn

        result = AdminRepository.find_admin_by_id(self.admin_id)
        self.assertIsNone(result)

    @patch("app.repositories.admin_repository.DB.get_db", side_effect=pymysql.MySQLError("bad query"))
    def test_find_admin_by_id_mysql_error(self, mock_get_db):
        with self.assertRaises(GenericDatabaseError):
            AdminRepository.find_admin_by_id(self.admin_id)

    # --- add_admin ---
    @patch("app.repositories.admin_repository.DB.get_db")
    def test_add_admin_success(self, mock_get_db):
        conn = MagicMock()
        cursor = MagicMock()
        cursor.rowcount = 1
        conn.cursor.return_value.__enter__.return_value = cursor
        mock_get_db.return_value = conn

        data = {"email": self.email, "username": "adminuser",
                "password_hash": "hashedpw"}
        result = AdminRepository.add_admin(data)

        cursor.execute.assert_called_once()
        conn.commit.assert_called_once()
        self.assertEqual(result, 1)

    @patch("app.repositories.admin_repository.DB.get_db", side_effect=pymysql.MySQLError("insert fail"))
    def test_add_admin_mysql_error(self, mock_get_db):
        data = {"email": self.email, "username": "adminuser",
                "password_hash": "hashedpw"}
        with self.assertRaises(GenericDatabaseError):
            AdminRepository.add_admin(data)

    # --- update_admin_status ---
    @patch("app.repositories.admin_repository.DB.get_db")
    def test_update_admin_status_success(self, mock_get_db):
        conn = MagicMock()
        cursor = MagicMock()
        cursor.fetchone.return_value = {"admin_id": self.admin_id}
        cursor.rowcount = 1
        conn.cursor.return_value.__enter__.return_value = cursor
        mock_get_db.return_value = conn

        result = AdminRepository.update_admin_status(self.email, 1)

        cursor.execute.assert_called()
        conn.commit.assert_called_once()
        self.assertEqual(result, 1)

    @patch("app.repositories.admin_repository.DB.get_db")
    def test_update_admin_status_not_found(self, mock_get_db):
        conn = MagicMock()
        cursor = MagicMock()
        cursor.fetchone.return_value = None
        conn.cursor.return_value.__enter__.return_value = cursor
        mock_get_db.return_value = conn

        result = AdminRepository.update_admin_status(self.email, 1)
        self.assertIsNone(result)

    @patch("app.repositories.admin_repository.DB.get_db", side_effect=pymysql.MySQLError("update fail"))
    def test_update_admin_status_mysql_error(self, mock_get_db):
        with self.assertRaises(GenericDatabaseError):
            AdminRepository.update_admin_status(self.email, 1)
