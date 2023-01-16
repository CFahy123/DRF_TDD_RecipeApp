"""
Tests for models
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal

from core import models

def create_user(email="user@exmaple.com", password="password123abc"):
    """Create and return a new user"""
    return get_user_model().objects.create_user(email, password)

class ModelTests(TestCase):
    """
    Tests for models
    """
    def test_create_user_with_email_successful(self):
        """Tests for create_user_with_email_successful"""
        email='test@example.com'
        password='testpass'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalization(self):
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@EXAMPLE.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.com', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com']
        ]

        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(
                email=email,
                password='testpass'
            )
            self.assertEqual(user.email, expected)


    def test_new_user_no_email(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                 email='',
                 password='testpass'
                )

        # try:
        #     get_user_model().objects.create_user(
        #         email='',
        #         password='testpass'
        #         )
        # except: self.assertRaises(ValueError)

    def test_create_new_superuser(self):
        """Tests for create_super_user"""
        email='supertest@example.com'
        password='testpass'
        user = get_user_model().objects.create_superuser(
            email=email,
            password=password,
        )

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_create_recipe(self):

        user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpass'
        )

        recipe = models.Recipe.objects.create(
            user=user,
            title='test recipe',
            description='test recipe description',
            time_minutes=5,
            price=Decimal('5.50')
        )

        self.assertEqual(str(recipe), recipe.title)


    def test_create_tag(self):
        user = create_user()
        tag = models.Tag.objects.create(
            user=user,
            name='Tag1'
        )

        self.assertEqual(str(tag), tag.name)


