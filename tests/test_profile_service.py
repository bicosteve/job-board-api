import unittest
from unittest.mock import patch
from app.services.profile_service import ProfileService
from app.utils.exceptions import GenericDatabaseError, InvalidCredentialsError


class TestProfileService(unittest.TestCase):

    def setUp(self):
        self.token = "validtoken"
        self.payload = {"first_name": "Steve",
                        "last_name": "Tester", "cv_url": "http://cv"}

    # --- create_profile tests ---
    @patch("app.services.profile_service.ProfileRepository.add_profile")
    @patch("app.services.profile_service.Security.decode_jwt_token")
    def test_create_profile_success(self, mock_decode, mock_add_profile):
        mock_decode.return_value = {"profile_id": 1}
        mock_add_profile.return_value = 1

        result = ProfileService.create_profile(self.token, self.payload)
        self.assertEqual(result, 1)

    @patch("app.services.profile_service.Security.decode_jwt_token")
    def test_create_profile_invalid_token(self, mock_decode):
        mock_decode.return_value = None
        with self.assertRaises(GenericDatabaseError):
            ProfileService.create_profile(self.token, self.payload)

    @patch("app.services.profile_service.Security.decode_jwt_token")
    def test_create_profile_missing_user_id(self, mock_decode):
        mock_decode.return_value = {"profile_id": None}
        with self.assertRaises(GenericDatabaseError):
            ProfileService.create_profile(self.token, self.payload)

    @patch("app.services.profile_service.ProfileRepository.add_profile")
    @patch("app.services.profile_service.Security.decode_jwt_token")
    def test_create_profile_not_created(self, mock_decode, mock_add_profile):
        mock_decode.return_value = {"profile_id": 1}
        mock_add_profile.return_value = 0

        result = ProfileService.create_profile(self.token, self.payload)
        self.assertEqual(result, 0)

    def test_create_profile_invalid_payload_type(self):
        with self.assertRaises(GenericDatabaseError):
            ProfileService.create_profile(self.token, "not_a_dict")

    # --- get_profile tests ---
    @patch("app.services.profile_service.ProfileRepository.get_profile")
    @patch("app.services.profile_service.Security.decode_jwt_token")
    def test_get_profile_success(self, mock_decode, mock_get_profile):
        mock_decode.return_value = {"profile_id": 1}
        mock_get_profile.return_value = {
            "first_name": "Steve", "last_name": "Tester"}

        profile = ProfileService.get_profile(self.token)
        self.assertEqual(profile["first_name"], "Steve")

    @patch("app.services.profile_service.Security.decode_jwt_token")
    def test_get_profile_invalid_token(self, mock_decode):
        mock_decode.return_value = None
        with self.assertRaises(InvalidCredentialsError):
            ProfileService.get_profile(self.token)

    @patch("app.services.profile_service.Security.decode_jwt_token")
    def test_get_profile_missing_user_id(self, mock_decode):
        mock_decode.return_value = {"profile_id": None}
        with self.assertRaises(InvalidCredentialsError):
            ProfileService.get_profile(self.token)

    @patch("app.services.profile_service.ProfileRepository.get_profile")
    @patch("app.services.profile_service.Security.decode_jwt_token")
    def test_get_profile_not_found(self, mock_decode, mock_get_profile):
        mock_decode.return_value = {"profile_id": 1}
        mock_get_profile.return_value = None

        with self.assertRaises(Exception) as ctx:
            ProfileService.get_profile(self.token)
        self.assertIn("Failed to get profile", str(ctx.exception))
