import unittest
from unittest.mock import patch

from app.services.user_service import UserService
from app.utils.exceptions import (
    GenericDatabaseError,
    InvalidCredentialsError,
    InvalidLoginAttemptError,
    UserExistError
)


class TestUserService(unittest.TestCase):
    def setUp(self):
        self.profile_id = 1
        self.email = 'test@example.com'
        self.hash = 'hashedpass'
        self.status = 1
        self.password = 'mypassword'
        self.created_at = '2025-01-01 12:00:00'

    @patch('app.services.user_service.UserRepository.find_user_by_id')
    def test_get_user_profile_returns_user_dict(self, mock_user_repo):
        fake_user = {
            'profile_id': self.profile_id,
            'email': self.email,
            'photo': 'http://example.com/photo.jpg',
            'status': 1,
            'reset_token': 'reset12345',
            'created_at': self.created_at,
            'modified_at': '2025-01-01 12:00:00'
        }

        mock_user_repo.return_value = fake_user

        result = UserService.get_user_profile(1)

        expected_keys = [
            'profile_id',
            'email',
            'photo',
            'status',
            'reset_token',
            'created_at',
            'modified_at',
        ]

        self.assertEqual(result['email'], fake_user['email'])
        self.assertListEqual(sorted(result.keys()), sorted(expected_keys))
        mock_user_repo.assert_called_once_with(1)

    @patch('app.services.user_service.UserRepository.find_user_by_id')
    def test_get_user_profile_raises_error_when_user_not_found(self, mock_user_repo):
        # Arrange
        mock_user_repo.return_value = None

        # Act & Assert
        with self.assertRaises(GenericDatabaseError) as context:
            UserService.get_user_profile(999)

        self.assertIn('error occurred while finding user',
                      str(context.exception))
        mock_user_repo.assert_called_once_with(999)

    @patch('app.services.user_service.Security.check_password', return_value=True)
    @patch('app.services.user_service.UserRepository.find_user_by_mail')
    def test_get_user_returns_user_success(self, mock_user_repo, mock_check_password):
        '''User exists, verified, and password matches'''
        user_data = {
            'profile_id': self.profile_id,
            'email': self.email,
            'hash': self.hash,
            'status': self.status,
            'created_at': self.created_at,
        }

        mock_user_repo.return_value = user_data

        user = UserService.get_user(self.email, self.password)

        self.assertEqual(user['email'], self.email)
        mock_user_repo.assert_called_once_with(self.email)
        mock_check_password.assert_called_once_with(
            self.password, 'hashedpass')

    @patch('app.services.user_service.Loggger.warn')
    @patch('app.services.user_service.UserRepository.find_user_by_mail', return_value=None)
    def test_get_user_not_found(self, mock_find_user, mock_warn):
        '''User not found'''

        mock_find_user.return_value = None

        with self.assertRaises(InvalidCredentialsError) as context:
            UserService.get_user(self.email, self.password)

        self.assertIn('Invalid email', str(context.exception))
        mock_warn.assert_called_once_with(
            f'user not found for email {self.email}')

    @patch('app.services.user_service.Loggger.warn')
    @patch('app.services.user_service.UserRepository.find_user_by_mail')
    def test_get_user_not_verified(self, mock_user, mock_warn):
        user_data = {
            'profile_id': self.profile_id,
            'email': self.email,
            'hash': self.hash,
            'status': self.status,
            'created_at': self.created_at
        }

        mock_user.return_value = {**user_data, 'status': 0}

        with self.assertRaises(InvalidLoginAttemptError) as ctx:
            UserService.get_user(self.email, self.password)

        self.assertIn('not verified', str(ctx.exception))
        mock_warn.assert_called_once_with(
            f'user not verified for {self.email}')

    @patch('app.services.user_service.Loggger.warn')
    @patch('app.services.user_service.Security.check_password', return_value=False)
    @patch('app.services.user_service.UserRepository.find_user_by_mail')
    def test_get_user_invalid_password(self, mock_find_user, mock_check_password, mock_warn):
        user_data = {
            'profile_id': self.profile_id,
            'email': self.email,
            'hash': self.hash,
            'status': self.status,
            'created_at': self.created_at
        }

        mock_find_user.return_value = user_data

        with self.assertRaises(InvalidCredentialsError) as ctx:
            UserService.get_user(self.email, 'wrongpass')

        self.assertIn('Invalid email or password', str(ctx.exception))
        mock_warn.assert_called_once_with(
            f'Invalid password for user {self.email}')
        mock_check_password.assert_called_once_with('wrongpass', 'hashedpass')

    @patch('app.services.user_service.Loggger.warn')
    @patch('app.services.user_service.Security.hash_password')
    @patch('app.services.user_service.UserRepository.find_user_by_mail')
    @patch('app.services.user_service.UserRepository.add_user')
    def test_register_user_success(self, mock_add_user, mock_find_user, mock_hash_password, mock_warn):

        # Arrange
        mock_find_user.return_value = None
        mock_hash_password.return_value = 'hashed_pass'
        mock_add_user.return_value = 1

        # Act
        result = UserService.register_user('Doe', self.email, self.password)

        # Assert
        mock_find_user.assert_called_once_with(self.email)
        mock_hash_password.assert_called_once_with(self.password)
        mock_add_user.assert_called_once_with(self.email, 'hashed_pass', 0)
        mock_warn.assert_not_called()
        self.assertEqual(result, {'rows_affected': 1})

    @patch('app.services.user_service.Loggger.warn')
    @patch('app.services.user_service.UserRepository.find_user_by_mail')
    def test_register_user_already_exist(self, mock_find_user, mock_warn):
        '''Test register user already existing'''
        mock_find_user.return_value = {'email': self.email}

        with self.assertRaises(UserExistError):
            UserService.register_user('Doe', self.email, self.password)

        mock_warn.assert_called_once_with(
            f'User already exist for email {self.email}')
