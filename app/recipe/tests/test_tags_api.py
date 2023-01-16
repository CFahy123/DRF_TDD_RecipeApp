from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from core.models import Tag
from recipe.serializers import TagSerializer


TAG_URL = reverse('recipe:tag-list')


def detail_url(tag_id):
    return reverse('recipe:tag-detail', args=[tag_id])


def create_user(email='usertest@test.com', password="pass123abc456"):
    """Create and return a new user"""
    return get_user_model().objects.create_user(email, password)


def create_tag(user):
    """Create and return a new tag"""

    tag = Tag.objects.create(user=user,name='Veggie')
    return tag

class PublicTagAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_unauthenticated_request(self):
        res = self.client.get(TAG_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagTests(TestCase):
    """test authenticated request"""
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)


    def test_tag_list(self):
        Tag.objects.create(user=self.user, name='Tag1')
        Tag.objects.create(user=self.user, name='Tag2')

        res =self.client.get(TAG_URL)
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)



    def test_tags_belong_to_user(self):
       other_user = create_user(email='other@example.com', password='otherpass123')

       tag = Tag.objects.create(user=self.user, name='Tag1')
       Tag.objects.create(user=other_user, name='Tag2')
       tags = Tag.objects.filter(user=self.user)
       serializer = TagSerializer(tags, many=True)

       res = self.client.get(TAG_URL)

       self.assertEqual(res.status_code, status.HTTP_200_OK)
       self.assertEqual(len(res.data), 1)
       self.assertEqual(res.data[0]['name'], tag.name)
       self.assertEqual(res.data, serializer.data)

     # test detail, create_tag, update, delete
    def test_tag_update(self):
        tag = Tag.objects.create(user=self.user, name='Breakfast')

        payload = {'name': 'New Tag'}
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(res.data['name'],payload['name'])


    def test_delete_tag(self):
        tag = Tag.objects.create(user=self.user, name='Breakfast')
        url = detail_url(tag.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Tag.objects.filter(id=tag.id).exists())

