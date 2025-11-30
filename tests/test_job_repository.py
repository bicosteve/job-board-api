import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, date

from app.repositories.jobs_repository import (
    JobRepository,
    serialize_job,
    convert_employment_type,
    convert_job_status,
)
from app.utils.exceptions import GenericDatabaseError


class TestHelpers(unittest.TestCase):
    def test_serialize_job_with_dates(self):
        row = {
            "job_id": 1,
            "deadline": date(2025, 12, 31),
            "created_at": datetime(2025, 1, 1, 10, 0),
            "updated_at": datetime(2025, 1, 2, 11, 0),
        }
        result = serialize_job(row)
        self.assertEqual(result["deadline"], "2025-12-31")
        self.assertTrue(result["created_at"].startswith("2025-01-01"))
        self.assertTrue(result["updated_at"].startswith("2025-01-02"))

    def test_convert_employment_type_valid(self):
        self.assertEqual(convert_employment_type("Full time"), "1")
        self.assertEqual(convert_employment_type("part time"), "2")

    def test_convert_employment_type_invalid(self):
        with self.assertRaises(ValueError):
            convert_employment_type("freelance")

    def test_convert_job_status_valid(self):
        self.assertEqual(convert_job_status("Open"), "5")
        self.assertEqual(convert_job_status("closed"), "6")

    def test_convert_job_status_invalid(self):
        with self.assertRaises(ValueError):
            convert_job_status("archived")


class TestJobRepository(unittest.TestCase):
    @patch("app.repositories.jobs_repository.DB.get_db")
    def test_insert_job_success(self, mock_get_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__.return_value = mock_cursor
        mock_cursor.lastrowid = 101
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        data = {
            "admin_id": 1,
            "title": "QA Engineer",
            "description": "Testing APIs",
            "requirements": "Python",
            "location": "Nairobi",
            "employment_type": "Full time",
            "salary_range": "1000-2000 USD",
            "company_name": "Shade Limited",
            "application_url": "https://example.com/apply",
            "deadline": "2025-12-31",
            "status": "Open",
        }

        result = JobRepository.insert_job(data)
        self.assertEqual(result, 101)
        mock_cursor.execute.assert_called()

    @patch("app.repositories.jobs_repository.DB.get_db")
    def test_get_jobs_success(self, mock_get_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            {"job_id": 1, "title": "QA Engineer",
                "deadline": date(2025, 12, 31)}
        ]
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        jobs = JobRepository.get_jobs(limit=10, offset=0)
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["title"], "QA Engineer")
        self.assertEqual(jobs[0]["deadline"], "2025-12-31")

    @patch("app.repositories.jobs_repository.DB.get_db")
    def test_get_job_success(self, mock_get_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {
            "job_id": 1,
            "title": "QA Engineer",
            "deadline": date(2025, 12, 31),
        }
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        job = JobRepository.get_job(1)
        self.assertEqual(job["job_id"], 1)
        self.assertEqual(job["deadline"], "2025-12-31")

    @patch("app.repositories.jobs_repository.DB.get_db")
    def test_get_job_not_found(self, mock_get_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        job = JobRepository.get_job(999)
        self.assertEqual(job, {})

    @patch("app.repositories.jobs_repository.DB.get_db")
    def test_update_job_success(self, mock_get_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__.return_value = mock_cursor
        mock_cursor.rowcount = 1
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        data = {"title": "Updated Job", "status": "Open"}
        result = JobRepository.update_job(1, 1, data)
        self.assertTrue(result)
        mock_cursor.execute.assert_called()

    @patch("app.repositories.jobs_repository.DB.get_db")
    def test_update_job_no_valid_fields(self, mock_get_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__.return_value = mock_cursor
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        with self.assertRaises(GenericDatabaseError):
            JobRepository.update_job(1, 1, {"invalid_field": "value"})
