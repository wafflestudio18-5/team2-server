from django.test import TestCase, Client
from rest_framework.authtoken.models import Token
from rest_framework import status
import json

from story.models import Story
from django.contrib.auth.models import User
from .constants import body_example

class DeleteStoryTestCase(TestCase):
    client = Client()

    def makeURI(self, pk):
        return f'/story/{pk}/'

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

    def test_delete_story(self):
        story = Story.objects.last() 
        response = self.client.delete(
            self.makeURI(story.id),
            HTTP_AUTHORIZATION=self.user_token
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_story_without_token(self):
        story = Story.objects.last() 
        response = self.client.delete(
            self.makeURI(story.id),
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_others_story(self):
        self.client.post(
            "/user/",
            json.dumps({
                "auth_type": "TEST",
                "username": "seoyoon2",
                "password": "password",
                "name": "Seoyoon",
                "email": "seoyoon2@wadium.shop",
                "profile_image": "https://wadium.shop/image/"
            }),
            content_type='application/json'
        )
        self.user2_token = 'Token ' + Token.objects.get(user__username='seoyoon2').key

        story = Story.objects.last() 
        response = self.client.delete(
            self.makeURI(story.id),
            HTTP_AUTHORIZATION=self.user2_token
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
