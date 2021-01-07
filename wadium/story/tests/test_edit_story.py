from django.test import TestCase, Client
from rest_framework.authtoken.models import Token
from rest_framework import status
import json
import datetime

from story.models import Story
from django.contrib.auth.models import User
from .utils import body_example

class EditStoryTestCase(TestCase):
    client = Client()

    def makeURI(self, pk):
        return f'/story/{pk}/'

    def setUp(self):
        # create user
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
                "title": "First Wadium Story",
                "subtitle": "This story has no content",
                "body": body_example,
                "featured_image": ""
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.user_token
        )

    def test_edit_story_all(self):
        story = Story.objects.last()
        response = self.client.put(
            self.makeURI(story.id),
            json.dumps({
                "title": "New Title",
                "subtitle": "New subtitle",
                "body": {},
                "featured_image": "https://wadium.shop/image/"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.user_token
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn("id", data)
        self.assertIn("writer", data)
        self.assertEqual(data["writer"]["username"], "seoyoon")
        self.assertEqual(data["title"], "New Title")
        self.assertEqual(data["subtitle"], "New subtitle")
        self.assertEqual(data["body"], {})
        self.assertEqual(data["featured_image"], 'https://wadium.shop/image/')
        self.assertFalse(data["published"])
        self.assertIn("created_at", data)
        self.assertIn("updated_at", data)
        self.assertEqual(data["published_at"], None)

        with self.subTest(msg='Checking DB'):
            story = Story.objects.last()
            self.assertEqual(story.title, "New Title")
            self.assertEqual(story.subtitle, "New subtitle")
            self.assertEqual(story.body, {})
            self.assertEqual(story.featured_image, "https://wadium.shop/image/")

    def test_edit_story_title(self):
        story = Story.objects.last()
        response = self.client.put(
            self.makeURI(story.id),
            json.dumps({
                "title": ""
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.user_token
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["title"], "Untitled")
        self.assertEqual(data["subtitle"], "This story has no content")
        self.assertEqual(data["body"], body_example)
        self.assertEqual(data["featured_image"], "")

        with self.subTest(msg='Checking DB'):
            story = Story.objects.last()
            self.assertEqual(story.title, "Untitled")
            self.assertEqual(story.subtitle, "This story has no content")
            self.assertEqual(story.body, body_example)
            self.assertEqual(story.featured_image, "")

    def test_edit_story_subtitle(self):
        story = Story.objects.last()
        response = self.client.put(
            self.makeURI(story.id),
            json.dumps({
                "subtitle": ""
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.user_token
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["title"], "First Wadium Story")
        self.assertEqual(data["subtitle"], "")
        self.assertEqual(data["body"], body_example)
        self.assertEqual(data["featured_image"], "")

        with self.subTest(msg='Checking DB'):
            story = Story.objects.last()
            self.assertEqual(story.title, "First Wadium Story")
            self.assertEqual(story.subtitle, "")
            self.assertEqual(story.body, body_example)
            self.assertEqual(story.featured_image, "")
        
    def test_edit_story_body(self):
        story = Story.objects.last()
        response = self.client.put(
            self.makeURI(story.id),
            json.dumps({
                "body": []
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.user_token
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["title"], "First Wadium Story")
        self.assertEqual(data["subtitle"], "This story has no content")
        self.assertEqual(data["body"], [])
        self.assertEqual(data["featured_image"], "")

        with self.subTest(msg='Checking DB'):
            story = Story.objects.last()
            self.assertEqual(story.title, "First Wadium Story")
            self.assertEqual(story.subtitle, "This story has no content")
            self.assertEqual(story.body, [])
            self.assertEqual(story.featured_image, "")
        
    def test_edit_story_image(self):
        story = Story.objects.last()    
        response = self.client.put(
            self.makeURI(story.id),
            json.dumps({
                "featured_image": "https://wadium.shop/image/"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.user_token
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["title"], "First Wadium Story")
        self.assertEqual(data["subtitle"], "This story has no content")
        self.assertEqual(data["body"], body_example)
        self.assertEqual(data["featured_image"], "https://wadium.shop/image/")

        with self.subTest(msg='Checking DB'):
            story = Story.objects.last()
            self.assertEqual(story.title, "First Wadium Story")
            self.assertEqual(story.subtitle, "This story has no content")
            self.assertEqual(story.body, body_example)
            self.assertEqual(story.featured_image, "https://wadium.shop/image/")

    def test_edit_story_invalid_URL(self):
        story = Story.objects.last()
        response = self.client.put(
            self.makeURI(story.id),
            json.dumps({
                "featured_image": "wadium.shop/image/"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.user_token
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        with self.subTest(msg='Checking DB'):
            story = Story.objects.last()
            self.assertEqual(story.featured_image, "")

    def test_edit_story_without_token(self):
        story = Story.objects.last()
        response = self.client.put(
            self.makeURI(story.id),
            json.dumps({
                "title": "",
                "body": []
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        with self.subTest(msg='Checking DB'):
            story = Story.objects.last()
            self.assertEqual(story.title, "First Wadium Story")
            self.assertEqual(story.body, body_example)

    def test_edit_others_story(self):
        self.client.post(
            '/user/',
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
        response = self.client.put(
            self.makeURI(story.id),
            json.dumps({
                "title": "",
                "body": []
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.user2_token
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        with self.subTest(msg='Checking DB'):
            story = Story.objects.last()
            self.assertEqual(story.title, "First Wadium Story")
            self.assertEqual(story.body, body_example)
