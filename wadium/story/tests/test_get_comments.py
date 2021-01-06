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

        for i in range(15):
            self.client.post(
                make_comment_URI(),
                json.dumps({
                    "body": f"Comment number {i}"
                }),
                content_type='application/json',
                HTTP_AUTHORIZATION=self.user2_token
            )
        self.assertEqual(StoryComment.objects.all().count(), 15)

    def test_get_comments(self):
        response = self.client.get(
            make_comment_URI()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        comment_count = StoryComment.objects.all().count()
        self.assertGreater(comment_count, 10)
        self.assertLessEqual(comment_count, 20)
        data = response.json()
        self.assertEqual(data['count'], comment_count)
        self.assertIsNotNone(data['next'])
        self.assertIsNone(data['previous'])
        self.assertEqual(len(data['comments']), 10)

        with self.subTest(msg='Test next page'):
            response = self.client.get(
                f'{make_comment_URI()}?page=2'
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = response.json()
            self.assertEqual(data['count'], comment_count)
            self.assertIsNone(data['next'])
            self.assertIsNotNone(data['previous'])
            self.assertEqual(len(data['comments']), comment_count-10)

    def test_get_comments_in_draft(self):
        story = Story.objects.last()
        self.client.post(
            f'/story/{story.id}/publish/',
            HTTP_AUTHORIZATION=self.user_token
        )
        response = self.client.get(
            make_comment_URI()
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
