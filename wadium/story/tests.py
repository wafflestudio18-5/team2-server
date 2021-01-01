from django.test import TestCase, Client
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework import status
import json
import datetime

from .models import Story
from django.contrib.auth.models import User

class PostStoryTestCase(TestCase):
    client = Client()
    reset_sequences = True
