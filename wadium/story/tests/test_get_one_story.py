from django.test import TestCase, Client
from rest_framework.authtoken.models import Token
from rest_framework import status
import json

from story.models import Story
from django.contrib.auth.models import User
from .constants import body_example

class GetOneStoryTestCase(TestCase):
    client = Client()

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
        story = Story.objects.last()
        self.client.post(
            f'/story/{story.id}/publish/',
            HTTP_AUTHORIZATION=self.user_token
        )

    def test_get_one_story(self):
        story = Story.objects.last()
        response = self.client.get(
            f'/story/{story.id}/'
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
        self.assertNotEqual(data["published_at"], None)

    def test_get_draft_story(self):
        story = Story.objects.last()
        self.client.post(
            f'/story/{story.id}/publish/',
            HTTP_AUTHORIZATION=self.user_token
        )
        response = self.client.get(
            f'/story/{story.id}/'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)