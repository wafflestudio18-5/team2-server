from django.test import TestCase, Client
from rest_framework.authtoken.models import Token
from rest_framework import status
import json
import datetime

from story.models import Story
from django.contrib.auth.models import User
from .constants import body_example

class PostStoryTestCase(TestCase):
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
    
    def test_post_story(self):
        # when all data are given
        response = self.client.post(
            '/story/',
            json.dumps({
                "title": "First Wadium Story",
                "subtitle": "This story has no content",
                "body": body_example,
                "featured_image": "https://wadium.shop/image/"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.user_token
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.json()
        self.assertIn("id", data)
        self.assertIn("writer", data) 
        self.assertEqual(data["writer"]["username"], "seoyoon")
        self.assertEqual(data["title"], "First Wadium Story")
        self.assertEqual(data["subtitle"], "This story has no content")
        self.assertEqual(data["body"], body_example)
        self.assertEqual(data["featured_image"], "https://wadium.shop/image/")
        self.assertFalse(data["published"])
        self.assertIn("created_at", data)
        self.assertIn("updated_at", data)
        self.assertEqual(data["published_at"], None)

        with self.subTest(msg='Checking DB - first story'):
            # Check if this story is saved in DB
            story = Story.objects.last()
            self.assertEqual(story.id, 1)
            self.assertEqual(story.title, "First Wadium Story")

        # with some blank values
        response = self.client.post(
            '/story/',
            json.dumps({
                "title": "",
                "subtitle": "",
                "body": [],
                "featured_image": ""
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.user_token
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.json()
        self.assertIn("id", data)
        self.assertIn("writer", data) 
        self.assertEqual(data["writer"]["username"], "seoyoon")
        self.assertEqual(data["title"], "Untitled")
        self.assertEqual(data["subtitle"], "")
        self.assertEqual(data["body"], [])
        self.assertEqual(data["featured_image"], "")
        self.assertFalse(data["published"])
        self.assertIn("created_at", data)
        self.assertIn("updated_at", data)
        self.assertEqual(data["published_at"], None)

        with self.subTest(msg='Checking DB - second story'):
            # Check if this story is saved in DB
            story = Story.objects.last()
            self.assertEqual(story.id, 2)
            self.assertEqual(story.title, "Untitled")

    def 
    # w/o title
        response = self.client.post(
            '/story/',
            json.dumps({
                "subtitle": "This story has no content",
                "body": body_example,
                "featured_image": "https://wadium.shop/image/"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.user_token
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
       
    def test_post_story_incomplete_request_no_body(self):
        # w/o body
        response = self.client.post(
            '/story/',
            json.dumps({
                "title": "Hello",
                "subtitle": "This story has no content",
                "featured_image": "https://wadium.shop/image/"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.user_token
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    
        # w/o featued_image
        response = self.client.post(
            '/story/',
            json.dumps({
                "title": "Hello",
                "subtitle": "This story has no content",
                "body": body_example,
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.user_token
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_post_story_incomplete_request_invalid_json(self):  
        # w/ invalid json
        response = self.client.post(
            '/story/',
            json.dumps({
                "title": "First Wadium Story",
                "subtitle": "This story has no content",
                "body": [', '[{"key": "value",}],
                "featured_image": "https://wadium.shop/image/"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.user_token
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_post_story_incomplete_request_invalid_url(self):    
        # w/ invalid url
        response = self.client.post(
            '/story/',
            json.dumps({
                "title": "First Wadium Story",
                "subtitle": "This story has no content",
                "body": body_example,
                "featured_image": "hello"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.user_token
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_story_without_token(self):
    # w/o title
        response = self.client.post(
            '/story/',
            json.dumps({
                "title": "First Wadium Story",
                "subtitle": "This story has no content",
                "body": body_example,
                "featured_image": "https://wadium.shop/image/"
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)