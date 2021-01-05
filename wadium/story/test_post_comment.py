from django.test import TransactionTestCase, Client
from rest_framework.authtoken.models import Token
from rest_framework import status
import json

from story.models import StoryComment
from django.contrib.auth.models import User
from .constants import body_example

class PostCommentTestCase(TransactionTestCase):
    client = Client()
    reset_sequences = True

    def setUp(self):
        self.client.post(
            "/user/",
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
            "/user/",
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

        self.client.post(
            '/story/',
            json.dumps({
                "title": "First Wadium Story",
                "subtitle": "This story has no content",
                "body": body_example,
                "featured_image": ""
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.user_token
        )

        self.client.post(
            '/story/1/publish/',
            HTTP_AUTHORIZATION=self.user_token
        )

    def test_post_comment(self):
        response = self.client.post(
            '/story/1/comment/',
            json.dumps({
                "body": "This is useful"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.user2_token
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertEqual(data['id'], 1)
        self.assertEqual(data['story_id'], 1)
        self.assertIn('writer', data)
        self.assertEqual(data['writer']['username'], 'seoyoon2')
        self.assertEqual(data['body'], "This is useful")
        self.assertIn('created_at', data)
        self.assertIn('updated_at', data)

        comment = StoryComment.objects.get(id=1)
        self.assertEqual(comment.story_id, 1)
        self.assertEqual(comment.body, "This is useful")