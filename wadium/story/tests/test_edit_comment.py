from django.test import TestCase, Client
from rest_framework.authtoken.models import Token
from rest_framework import status
import json

from story.models import Story, StoryComment
from django.contrib.auth.models import User
from .utils import body_example, make_comment_URI

class EditCommentTestCase(TestCase):
    client = Client()

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

        story = Story.objects.last()
        self.client.post(
            f'/story/{story.id}/publish/',
            HTTP_AUTHORIZATION=self.user_token
        )

        self.client.post(
            make_comment_URI(),
            json.dumps({
                "body": "This is useful"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.user2_token
        )

    def test_edit_comment(self):
        comment = StoryComment.objects.last()
        response = self.client.put(
            make_comment_URI(comment.id),
            json.dumps({
                "body": "New comment!"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.user2_token
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn('id', data)
        self.assertIn('story_id', data)
        self.assertIn('writer', data)
        self.assertEqual(data['writer']['username'], 'seoyoon2')
        self.assertEqual(data['body'], "New comment!")
        self.assertIn('created_at', data)
        self.assertIn('updated_at', data)

        with self.subTest(msg='Checking DB'):
            comment = StoryComment.objects.last()
            self.assertEqual(comment.body, "New comment!")

    def test_edit_comment_without_body(self):
        comment = StoryComment.objects.last()
        response = self.client.put(
            make_comment_URI(comment.id),
            json.dumps({
                
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.user2_token
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK) # because of partial=True serializer
        with self.subTest(msg='Checking DB'):
            comment = StoryComment.objects.last()
            self.assertEqual(comment.body, "This is useful")

    def test_edit_comment_blank_body(self):
        comment = StoryComment.objects.last()
        response = self.client.put(
            make_comment_URI(comment.id),
            json.dumps({
                "body": ""
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.user2_token
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_edit_comment_without_token(self):
        comment = StoryComment.objects.last()
        response = self.client.put(
            make_comment_URI(comment.id),
            json.dumps({
                "body": "New comment!"
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_edit_others_comment(self):
        comment = StoryComment.objects.last()
        response = self.client.put(
            make_comment_URI(comment.id),
            json.dumps({
                "body": "New comment!"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.user_token
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)