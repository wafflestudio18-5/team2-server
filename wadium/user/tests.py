from django.test import SimpleTestCase
from .models import EmailAuth, generate_token, EmailAddress
from django.utils import timezone
import datetime


class EmailAuthTestCase(SimpleTestCase):
    def test_generate_token(self):
        valid_chars = '0123456789abcdef'
        token = generate_token()
        self.assertEqual(len(token), 12)
        self.assertLessEqual(set(token), set(valid_chars))

    def test_default_token(self):
        valid_chars = '0123456789abcdef'
        email_auth = EmailAuth()
        token = email_auth.token
        self.assertEqual(len(token), 12)
        self.assertLessEqual(set(token), set(valid_chars))

    def test_expired_false(self):
        email_auth = EmailAuth()
        email_auth.expires_at = timezone.now() + datetime.timedelta(minutes=1)
        self.assertFalse(email_auth.expired)

    def test_expired_true(self):
        email_auth = EmailAuth()
        email_auth.expires_at = timezone.now() + datetime.timedelta(minutes=-1)
        self.assertTrue(email_auth.expired)


class EmailAddressTestCase(SimpleTestCase):
    def test_email_address_str(self):
        email = 'test@example.com'
        email_address = EmailAddress(email=email)
        self.assertEqual(str(email_address), email)
