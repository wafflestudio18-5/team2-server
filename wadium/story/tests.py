from django.test import SimpleTestCase, TestCase, Client
from .models import Story
from django.contrib.auth.models import User
from django.utils import timezone
import datetime
from rest_framework.authtoken.models import Token
from rest_framework import status
import json