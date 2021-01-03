from django.test import TransactionTestCase, Client
from rest_framework.authtoken.models import Token
from rest_framework import status
import json
import datetime

from story.models import Story
from django.contrib.auth.models import User

class PostStoryTestCase(TransactionTestCase):
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
        # create users
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
            '/user/',
            json.dumps({
                "auth_type": "TEST",
                "username": "seoyoon2",
                "password": "password",
                "name": "Seoyoon Moon",
                "email": "seoyoon2@wadium.shop",
                "profile_image": "https://wadium.shop/image/"
            }),
            content_type='application/json'
        )
        self.user2_token = 'Token ' + Token.objects.get(user__username='seoyoon2').key


    def test_edit_story(self):
        # create one story
        self.client.post(
            '/story/',
            json.dumps({
                "title": "First Wadium Story",
                "subtitle": "This story has no content",
                "body": self.body_example,
                "featured_image": ""
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.user_token
        )
        self.assertEqual(Story.objects.count(), 1)
        self.assertEqual(Story.objects.get(title="First Wadium Story").id, 1)

        response = self.client.put(
            '/story/1/',
            json.dumps({
                "title": "New Title",
                "subtitle": "This story has no content",
                "body": {},
                "featured_image": "https://wadium.shop/image/"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.user_token
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn("id", data)
        self.assertEqual(data['id'], 1)
        self.assertIn("writer", data)
        self.assertEqual(data["writer"]["username"], "seoyoon")
        self.assertEqual(data["title"], "New Title")
        self.assertEqual(data["subtitle"], "This story has no content")
        self.assertEqual(data["body"], {})
        self.assertEqual(data["featured_image"], 'https://wadium.shop/image/')
        self.assertFalse(data["published"])
        self.assertIn("created_at", data)
        self.assertIn("updated_at", data)
        self.assertIn("published_at", data)

        story = Story.objects.get(id=1)
        self.assertEqual(story.title, "New Title")