from django.test import TransactionTestCase, Client
from rest_framework.authtoken.models import Token
from rest_framework import status
import json

from story.models import Story
from django.contrib.auth.models import User

class PublishStoryTestCase(TransactionTestCase):
    client = Client()
    reset_sequences = True
    body_example = [
        [
            {
                "type": "paragraph",
                "detail": {
                    "content": "Wadium",
                    "emphasizing": "large"
                }
            },
            {
                "type": "paragraph",
                "detail": {
                    "content": "Normal <em>hello! <strong>asdbasdnb</strong>asdbpoiahsb</em>",
                    "emphasizing": "normal"
                }
            },
            {
                "type": "image",
                "detail": {
                    "size": "normal",
                    "imgsrc": "https://wadium.shop/image/",
                    "content": "image caption"
                }
            }
        ]
    ]

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
                "body": self.body_example,
                "featured_image": "",
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.user_token
        )

    def test_publish_story(self):
        self.assertEqual(Story.objects.count(), 1)
        self.assertEqual(Story.objects.get(title="Hello").id, 1)

        response = self.client.post(
            '/story/1/publish/',
            HTTP_AUTHORIZATION=self.user_token
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn("id", data)
        self.assertEqual(data['id'], 1)
        self.assertIn("writer", data)
        self.assertEqual(data["writer"]["username"], "seoyoon")
        self.assertEqual(data["title"], "Hello")
        self.assertEqual(data["subtitle"], "Say hello!")
        self.assertEqual(data["body"], self.body_example)
        self.assertEqual(data["featured_image"], "")
        self.assertIn("created_at", data)
        self.assertIn("updated_at", data)

        self.assertTrue(data["published"])
        self.assertNotEqual(data["published_at"], None)

        story = Story.objects.get(id=1)
        self.assertTrue(story.published)
        self.assertNotEqual(story.published_at, None)

    def test_publish_story_without_token(self):
        response = self.client.post(
            '/story/1/publish/',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

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

        response = self.client.post(
            '/story/1/publish/',
            HTTP_AUTHORIZATION=self.user2_token
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)