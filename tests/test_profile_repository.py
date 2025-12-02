import unittest
from unittest.mock import patch, MagicMock
from datetime import date

from app.repositories.profile_repository import ProfileRepository
from app.utils.exceptions import GenericDatabaseError


class TestProfileRepository(unittest.TestCase):

    @patch("app.repositories.profile_repository.DB.get_db")
    def test_add_profile_success(self, mock_get_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__.return_value = mock_cursor
        mock_cursor.rowcount = 1
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        data = {"first_name": "Steve",
                "last_name": "Tester", "cv_url": "http://cv"}
        result = ProfileRepository.add_profile(1, data)

        self.assertEqual(result, 1)
        mock_cursor.execute.assert_called()
        mock_conn.commit.assert_called()

    @patch("app.repositories.profile_repository.DB.get_db")
    def test_add_profile_invalid_data(self, mock_get_db):
        mock_get_db.return_value = MagicMock()
        with self.assertRaises(GenericDatabaseError):
            ProfileRepository.add_profile(1, "not_a_dict")

    @patch("app.repositories.profile_repository.DB.get_db")
    def test_get_profile_success(self, mock_get_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {
            "first_name": "Steve",
            "last_name": "Tester",
            "cv_url": "http://cv",
            "level": "Bachelor",
            "institution": "University",
            "field": "CS",
            "start_date": date(2020, 1, 1),
            "end_date": date(2024, 1, 1),
            "description": "Graduate",
        }
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        profile = ProfileRepository.get_profile(1)
        self.assertEqual(profile["first_name"], "Steve")
        self.assertEqual(profile["cv_url"], "http://cv")
        self.assertEqual(profile["start_date"], "2020-01-01")
        self.assertEqual(profile["end_date"], "2024-01-01")

    @patch("app.repositories.profile_repository.DB.get_db")
    def test_get_profile_not_found(self, mock_get_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        profile = ProfileRepository.get_profile(999)
        self.assertIsNone(profile)

    @patch("app.repositories.profile_repository.DB.get_db")
    def test_add_profile_db_error(self, mock_get_db):
        mock_conn = MagicMock()
        mock_conn.cursor.side_effect = Exception("DB error")
        mock_get_db.return_value = mock_conn

        data = {"first_name": "Steve", "last_name": "Tester", "cv_url": ""}
        with self.assertRaises(GenericDatabaseError):
            ProfileRepository.add_profile(1, data)

    @patch("app.repositories.profile_repository.DB.get_db")
    def test_get_profile_db_error(self, mock_get_db):
        mock_conn = MagicMock()
        mock_conn.cursor.side_effect = Exception("DB error")
        mock_get_db.return_value = mock_conn

        with self.assertRaises(GenericDatabaseError):
            ProfileRepository.get_profile(1)
