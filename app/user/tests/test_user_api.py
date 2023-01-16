"""
Tests for the user API
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient


CREATE_USER_URL = reverse('user:create')
CREATE_TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')

def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)

class PublicUserApiTests(TestCase):
    """Tests for public features of the API"""
    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """Test creating a user is successful"""
        payload = {
            'name': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword123',
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_with_email_exists_error(self):
        """Test creating a user with an existing email"""
        payload = {
            'name': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword123',
        }

        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


    def test_password_too_short_error(self):
        """Test creating a user with an existing email"""
        payload = {
            'name': 'testuser',
            'email': 'test@example.com',
            'password': 'pw',
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        user_details = {
            'name': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword123',
        }
        create_user(**user_details)

        payload = {
            'email': user_details['email'],
            'password': user_details['password']
        }

        res = self.client.post(CREATE_TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credentials(self):
        user_details = {
        'name': 'testuser',
        'email': 'test@example.com',
        'password': 'testpassword123',
        }
        create_user(**user_details)

        payload = {
            'email':'test@example.com',
            'password': 'fake12345'
        }

        res = self.client.post(CREATE_TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        user_details = {
        'name': 'testuser',
        'email': 'test@example.com',
        'password': 'testpassword123',
        }
        create_user(**user_details)

        payload = {
            'email':'test@example.com',
            'password': ''
        }

        res = self.client.post(CREATE_TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrive_user_unauthorized(self):
        """Test authentication is required for users"""
        res = self.client.post(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTest(TestCase):
    """test features which requre authentication"""
    def setUp(self):

        user_details = {
        'name': 'testuser',
        'email': 'test@example.com',
        'password': 'testpassword123',
        }
        self.user = create_user(**user_details)

        self.client =APIClient()
        self.client.force_authenticate(user=self.user)


    def test_retieve_profile_success(self):
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['name'], self.user.name)
        self.assertEqual(res.data['email'], self.user.email)

    def test_post_me_not_allowed(self):
        res = self.client.post(ME_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


    def test_update_user_profile(self):
        payload = {'name': 'updatename', 'password': 'newpass2344'}

        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)