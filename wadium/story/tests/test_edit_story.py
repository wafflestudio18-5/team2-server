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

    def test_edit_story(self):
        # create one story
        self.assertEqual(Story.objects.count(), 1)
        self.assertEqual(Story.objects.get(title="First Wadium Story").id, 1)

        response = self.client.put(
            '/story/1/',
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
        self.assertEqual(data['id'], 1)
        self.assertIn("writer", data)
        self.assertEqual(data["writer"]["username"], "seoyoon")
        self.assertEqual(data["title"], "New Title")
        self.assertEqual(data["subtitle"], "New subtitle")
        self.assertEqual(data["body"], {})
        self.assertEqual(data["featured_image"], 'https://wadium.shop/image/')
        self.assertFalse(data["published"])
        self.assertIn("created_at", data)
        self.assertIn("updated_at", data)
        self.assertIn("published_at", data)

        story = Story.objects.get(id=1)
        self.assertEqual(story.title, "New Title")

        response = self.client.put(
            '/story/1/',
            json.dumps({
                "title": ""
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.user_token
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["title"], "Untitled")
        self.assertEqual(data["subtitle"], "New subtitle")
        self.assertEqual(data["body"], {})
        self.assertEqual(data["featured_image"], 'https://wadium.shop/image/')
        story = Story.objects.get(id=1)
        self.assertEqual(story.title, "Untitled")

        response = self.client.put(
            '/story/1/',
            json.dumps({
                "subtitle": ""
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.user_token
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["title"], "Untitled")
        self.assertEqual(data["subtitle"], "")
        self.assertEqual(data["body"], {})
        self.assertEqual(data["featured_image"], 'https://wadium.shop/image/')
        
        response = self.client.put(
            '/story/1/',
            json.dumps({
                "body": []
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.user_token
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["title"], "Untitled")
        self.assertEqual(data["subtitle"], "")
        self.assertEqual(data["body"], [])
        self.assertEqual(data["featured_image"], 'https://wadium.shop/image/')
        
        response = self.client.put(
            '/story/1/',
            json.dumps({
                "featured_image": ""
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.user_token
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["title"], "Untitled")
        self.assertEqual(data["subtitle"], "")
        self.assertEqual(data["body"], [])
        self.assertEqual(data["featured_image"], "")
        

    def test_edit_story_without_token(self):
        response = self.client.put(
            '/story/1/',
            json.dumps({
                "title": "",
                "body": []
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        story = Story.objects.get(id=1)
        self.assertEqual(story.title, "First Wadium Story")
        self.assertEqual(story.body, self.body_example)

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
        
        response = self.client.put(
            '/story/1/',
            json.dumps({
                "title": "",
                "body": []
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.user2_token
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        story = Story.objects.get(id=1)
        self.assertEqual(story.title, "First Wadium Story")
        self.assertEqual(story.body, self.body_example)
