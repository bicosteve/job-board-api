import unittest
from unittest.mock import patch, MagicMock
import pymysql


from app.repositories.user_repository import UserRepository
from app.utils.exceptions import GenericDatabaseError


class TestUserRepository(unittest.TestCase):

    def test_find_user_by_mail_success(self):
        '''Should return user object'''
        # Arrange
        fake_user = {
            'profile_id': 1,
            'email': 'test@example.com',
            'hash': 'somehash',
            'status': 1,
            'created_at': '2025-10-25 00:00:00'
        }

        with patch('app.repositories.user_repository.DB.get_db') as mock_get_db:

            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = fake_user
            mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
            mock_get_db.return_value = mock_conn

            # Act
            result = UserRepository.find_user_by_mail('test@example.com')

            # Assert
            mock_cursor.execute.assert_called_once()
            mock_cursor.fetchone.assert_called_once()
            self.assertIsInstance(result, dict)
            self.assertEqual(result['email'], 'test@example.com')
            self.assertEqual(result['status'], 1)
            self.assertEqual(result['profile_id'], 1)
            self.assertIn('hash', result)

    def test_find_user_by_mail_not_found(self):
        '''Should return None if no user is found'''

        # Arrange
        email = 'error@example.com'

        with patch('app.repositories.user_repository.DB.get_db') as mock_get_db:
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
        '''Raise GenericDatabaseError on Mysql error'''
        email = 'error@example.com'

        with patch('app.repositories.user_repository.DB.get_db') as mock_get_db:
            mock_get_db.side_effect = pymysql.MySQLError(
                'DB connection failed')

            with self.assertRaises(GenericDatabaseError):
                UserRepository.find_user_by_mail(email)

    def test_find_user_by_mail_generic_exception(self):
        '''Should raise GenericDatabaseError on unexpected error'''
        email = 'error@example.com'

        with patch('app.repositories.user_repository.DB.get_db') as mock_get_db:
            mock_get_db.side_effect = Exception('Something broke')

            with self.assertRaises(GenericDatabaseError):
                UserRepository.find_user_by_mail(email)

    def test_find_user_by_id_success(self):
        '''Should return user object if success'''
        profile_id = 1
        fake_user = {
            'profile_id': profile_id,
            'email': 'test@example.com',
            'photo': 'https://picsum.photos/200/300',
            'status': 1,
            'reset_token': 'some-reset-token',
            'created_at': '2025-10-25 00:00:00',
            'updated_at': '2025-10-25 00:00:00',
        }

        with patch('app.repositories.user_repository.DB.get_db') as mock_get_db:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = fake_user
            mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
            mock_get_db.return_value = mock_conn

            # Act
            result = UserRepository.find_user_by_id(profile_id)

            # Assert
            mock_cursor.execute.assert_called_once()
            mock_cursor.fetchone.assert_called_once()
            self.assertIsInstance(result, dict)
            self.assertEqual(fake_user['profile_id'], 1)

    def test_find_user_by_id_not_found(self):
        '''Shoud return None'''
        id = 1

        with patch('app.repositories.user_repository.DB.get_db') as mock_get_db:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()

            mock_cursor.fetchone.return_value = None
            mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
            mock_get_db.return_value = mock_conn

            result = UserRepository.find_user_by_id(id)

            mock_cursor.execute.assert_called_once()
            self.assertIsNone(result)
