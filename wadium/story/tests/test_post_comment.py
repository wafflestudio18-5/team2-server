from django.test import TestCase, Client
from rest_framework.authtoken.models import Token
from rest_framework import status
import json

from story.models import Story, StoryComment
from django.contrib.auth.models import User
from .utils import body_example, make_comment_URI

class PostCommentTestCase(TestCase):
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

    def test_post_comment(self):
        response = self.client.post(
            make_comment_URI(),
            json.dumps({
                "body": "This is useful"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.user2_token
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertIn('id', data)
        self.assertIn('story_id', data)
        self.assertIn('writer', data)
        self.assertEqual(data['writer']['username'], 'seoyoon2')
        self.assertEqual(data['body'], "This is useful")
        self.assertIn('created_at', data)
        self.assertIn('updated_at', data)

        with self.subTest(msg='Checking DB'):
            comment = StoryComment.objects.last()
            self.assertEqual(comment.body, "This is useful")

    def test_post_comment_to_oneself(self):
        response = self.client.post(
            make_comment_URI(),
            json.dumps({
                "body": "Thank you!"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.user_token
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertIn('id', data)
        self.assertIn('story_id', data)
        self.assertIn('writer', data)
        self.assertEqual(data['writer']['username'], 'seoyoon')
        self.assertEqual(data['body'], "Thank you!")
        self.assertIn('created_at', data)
        self.assertIn('updated_at', data)

        with self.subTest(msg='Checking DB'):
            comment = StoryComment.objects.last()
            self.assertEqual(comment.body, "Thank you!")

    def test_post_comment_to_draft(self):
        story = Story.objects.last()
        self.client.post(
            f'/story/{story.id}/publish/',
            HTTP_AUTHORIZATION=self.user_token
        )
        story = Story.objects.last()
        assert not story.published # assert that this is a draft

        response = self.client.post(
            make_comment_URI(),
            json.dumps({
                "body": "Great job!"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.user2_token
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_comment_without_token(self):
        response = self.client.post(
            make_comment_URI(),
            json.dumps({
                "body": "Great job!"
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_comment_without_body(self):
        response = self.client.post(
            make_comment_URI(),
            json.dumps({
                
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.user2_token
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_post_comment_blank_body(self):
        response = self.client.post(
            make_comment_URI(),
            json.dumps({
                "body": ""
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.user2_token
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
