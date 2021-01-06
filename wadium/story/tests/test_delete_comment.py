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
        
        self.begining_num = 5
        for i in range(self.begining_num):
            self.client.post(
                make_comment_URI(),
                json.dumps({
                    "body": f"Comment number {i}"
                }),
                content_type='application/json',
                HTTP_AUTHORIZATION=self.user2_token
            )

    def test_delete_comment(self):
        comment = StoryComment.objects.last()
        response = self.client.delete(
            make_comment_URI(comment.id),
            HTTP_AUTHORIZATION=self.user2_token
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(StoryComment.objects.count(), self.begining_num-1)
    
    def test_delete_comment_draft(self):
        story = Story.objects.last()
        self.client.post(
            f'/story/{story.id}/publish/',
            HTTP_AUTHORIZATION=self.user_token
        )
        
        comment = StoryComment.objects.last()
        response = self.client.delete(
            make_comment_URI(comment.id),
            HTTP_AUTHORIZATION=self.user2_token
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(StoryComment.objects.count(), self.begining_num)
    
    def test_delete_comment_without_token(self):
        comment = StoryComment.objects.last()
        response = self.client.delete(
            make_comment_URI(comment.id)
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(StoryComment.objects.count(), self.begining_num)
    
    def test_delete_others_comment(self):
        comment = StoryComment.objects.last()
        response = self.client.delete(
            make_comment_URI(comment.id),
            HTTP_AUTHORIZATION=self.user_token
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(StoryComment.objects.count(), self.begining_num)