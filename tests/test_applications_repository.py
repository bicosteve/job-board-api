import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from app.repositories.applications_repository import (
    ApplicationRepository,
    serialize_application,
)
from app.utils.exceptions import GenericDatabaseError


class TestSerializeApplication(unittest.TestCase):
    def test_serialize_application_with_dates(self):
        row = {
            "application_id": 1,
            "created_at": datetime(2025, 1, 1, 10, 0),
            "modified_at": datetime(2025, 1, 2, 11, 0),
        }
        result = serialize_application(row)
        self.assertEqual(result["created_at"], "2025-01-01T10:00:00")
        self.assertEqual(result["modified_at"], "2025-01-02T11:00:00")


class TestApplicationRepository(unittest.TestCase):
    @patch("app.repositories.applications_repository.DB.get_db")
    def test_create_application_success(self, mock_get_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__.return_value = mock_cursor
        mock_cursor.lastrowid = 123
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        data = {
            "job_id": 1,
            "status": 1,
            "cover_letter": "Interested",
            "resume_url": "http://resume",
        }
        result = ApplicationRepository.create_application(1, data)
        self.assertEqual(result, 123)
        mock_cursor.execute.assert_called()
        mock_conn.commit.assert_called()

    @patch("app.repositories.applications_repository.DB.get_db")
    def test_get_jobs_applications_success(self, mock_get_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            {"application_id": 1, "created_at": datetime(2025, 1, 1)}
        ]
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        result = ApplicationRepository.get_jobs_applications(1, 10, 0)
        self.assertEqual(result[0]["created_at"], "2025-01-01T00:00:00")

    @patch("app.repositories.applications_repository.DB.get_db")
    def test_get_user_application_success(self, mock_get_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {
            "application_id": 1,
            "created_at": datetime(2025, 1, 1),
        }
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        result = ApplicationRepository.get_user_application(1, 1)
        self.assertEqual(result["created_at"], "2025-01-01T00:00:00")

    @patch("app.repositories.applications_repository.DB.get_db")
    def test_get_user_application_not_found(self, mock_get_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        result = ApplicationRepository.get_user_application(1, 1)
        self.assertEqual(result, {})

    @patch("app.repositories.applications_repository.DB.get_db")
    def test_get_user_applications_success(self, mock_get_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            {"application_id": 1, "created_at": datetime(2025, 1, 1)}
        ]
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        result = ApplicationRepository.get_user_applications(1)
        self.assertEqual(result[0]["created_at"], "2025-01-01T00:00:00")

    @patch("app.repositories.applications_repository.DB.get_db")
    def test_update_application_success(self, mock_get_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__.return_value = mock_cursor
        mock_cursor.rowcount = 1
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        result = ApplicationRepository.update_application(1, 1, 2)
        self.assertTrue(result)
        mock_cursor.execute.assert_called()
        mock_conn.commit.assert_called()

    @patch("app.repositories.applications_repository.DB.get_db")
    def test_update_application_failure(self, mock_get_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__.return_value = mock_cursor
        mock_cursor.rowcount = 0
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        result = ApplicationRepository.update_application(1, 1, 2)
        self.assertFalse(result)

    @patch("app.repositories.applications_repository.DB.get_db")
    def test_create_application_db_error(self, mock_get_db):
        mock_conn = MagicMock()
        mock_conn.cursor.side_effect = Exception("DB error")
        mock_get_db.return_value = mock_conn

        data = {"job_id": 1, "status": 1, "cover_letter": "", "resume_url": ""}
        with self.assertRaises(GenericDatabaseError):
            ApplicationRepository.create_application(1, data)
