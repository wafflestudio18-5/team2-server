from django.test import TestCase, Client
from rest_framework.authtoken.models import Token
from rest_framework import status
import json

from story.models import Story
from django.contrib.auth.models import User
from .utils import body_example

class PublishStoryTestCase(TestCase):
    client = Client()

    def makeURI(self, pk):
        return f'/story/{pk}/publish/'

    def setUp(self):
        self.client.post(
            '/user/',
            json.dumps({
                "auth_type": "TEST",
                "username": "seoyoon",
                "password": "password",
                "name": "Seoyoon Moon",
                "email": "seoyoon@wadium.shop",
                "profile_image": "https://wadium.shop/image/"
            }),
            content_type='application/json'
        )
        self.user_token = 'Token ' + Token.objects.get(user__username='seoyoon').key

        self.client.post(
            '/story/',
            json.dumps({
                "title": "Hello",
                "subtitle": "Say hello!",
                "body": body_example,
                "featured_image": "",
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.user_token
        )

    def test_publish_story(self):
        story = Story.objects.last()
        response = self.client.post(
            self.makeURI(story.id),
            HTTP_AUTHORIZATION=self.user_token
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn("id", data)
        self.assertIn("writer", data)
        self.assertEqual(data["writer"]["username"], "seoyoon")
        self.assertEqual(data["title"], "Hello")
        self.assertEqual(data["subtitle"], "Say hello!")
        self.assertEqual(data["body"], body_example)
        self.assertEqual(data["featured_image"], "")
        self.assertIn("created_at", data)
        self.assertIn("updated_at", data)

        self.assertTrue(data["published"])
        self.assertIsNotNone(data["published_at"])

        with self.subTest(msg='Cheking DB'):
            story = Story.objects.last()
            self.assertTrue(story.published)
            self.assertIsNotNone(story.published_at)

        # unpublish again
        response = self.client.post(
            self.makeURI(story.id),
            HTTP_AUTHORIZATION=self.user_token
        )
        data = response.json()
        self.assertFalse(data["published"])
        self.assertIsNone(data["published_at"])

        with self.subTest(msg='Cheking DB'):
            story = Story.objects.last()
            self.assertFalse(story.published)
            self.assertIsNone(story.published_at)

    def test_publish_story_without_token(self):
        story = Story.objects.last()
        response = self.client.post(
            self.makeURI(story.id)
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        with self.subTest(msg='Cheking DB'):
            story = Story.objects.last()
            self.assertFalse(story.published)
            self.assertIsNone(story.published_at)

    def test_puslish_others_story(self):
        self.client.post(
            '/user/',
            json.dumps({
                "auth_type": "TEST",
                "username": "seoyoon2",
                "password": "password",
                "name": "Seoyoon2",
                "email": "seoyoon2@wadium.shop",
                "profile_image": "https://wadium.shop/image/"
            }),
            content_type='application/json'
        )
        self.user2_token = 'Token ' + Token.objects.get(user__username='seoyoon2').key

        story = Story.objects.last()
        response = self.client.post(
            self.makeURI(story.id),
            HTTP_AUTHORIZATION=self.user2_token
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        with self.subTest(msg='Cheking DB'):
            story = Story.objects.last()
            self.assertFalse(story.published)
            self.assertIsNone(story.published_at)