from django.test import SimpleTestCase, TestCase
from .models import EmailAuth, generate_token, EmailAddress, UserProfile
from django.contrib.auth.models import User
from django.utils import timezone
import datetime
from rest_framework.authtoken.models import Token
from rest_framework import status


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


class EmailAddressTestCase(TestCase):
    def test_email_address_str(self):
        email = 'test@example.com'
        email_address = EmailAddress(email=email)
        self.assertEqual(str(email_address), email)

    def test_email_address_available(self):
        email = 'test@example.com'
        email_address = EmailAddress.objects.create(email=email)
        self.assertTrue(email_address.available)

    def test_email_address_not_available(self):
        user = User.objects.create(username='test', password=UserProfile.NORMAL_PW)
        email = 'test@example.com'
        email_address = EmailAddress.objects.create(email=email, user=user)
        self.assertFalse(email_address.available)


class CreateUserTestCase(TestCase):
    username = 'test'
    userprofile = {
        'name': 'Test User',
        'profile_image': 'https://example.com/image',
        'email': 'test@example.com'
    }

    def test_create_user(self):
        user = UserProfile.create_user(self.username, self.userprofile)
        self.assertTrue(hasattr(user, 'userprofile'))
        for key, value in self.userprofile.items():
            self.assertEqual(getattr(user.userprofile, key), value)
        self.assertTrue(hasattr(user, 'emails'))
        self.assertEqual(user.emails.count(), 1)
        email_address = user.emails.get()
        self.assertTrue(email_address.primary)
        self.assertEqual(email_address.email, self.userprofile['email'])

    def test_create_user_required_field(self):
        userprofile = {
            'name': 'Test User',
            'email': 'test@example.com'
        }
        user = UserProfile.create_user(self.username, userprofile)
        self.assertTrue(hasattr(user, 'userprofile'))
        for key, value in userprofile.items():
            self.assertEqual(getattr(user.userprofile, key), value)
        self.assertTrue(hasattr(user, 'emails'))
        self.assertEqual(user.emails.count(), 1)
        email_address = user.emails.get()
        self.assertTrue(email_address.primary)
        self.assertEqual(email_address.email, userprofile['email'])

    def test_create_test_user(self):
        user = UserProfile.create_user(self.username, self.userprofile, test_user=True)
        self.assertTrue(hasattr(user, 'userprofile'))
        for key, value in self.userprofile.items():
            self.assertEqual(getattr(user.userprofile, key), value)
        self.assertTrue(hasattr(user, 'emails'))
        self.assertEqual(user.emails.count(), 1)
        email_address = user.emails.get()
        self.assertTrue(email_address.primary)
        self.assertEqual(email_address.email, self.userprofile['email'])

    def test_user_email_address(self):
        user = UserProfile.create_user(self.username, self.userprofile)
        email_address = EmailAddress.objects.get(user=user)
        EmailAddress.objects.create(email='test2@example.com', user=user, primary=False)
        self.assertEqual(user.emails.count(), 2)
        self.assertEqual(user.userprofile.email_address, email_address)
        self.assertEqual(user.userprofile.email, self.userprofile['email'])


class TESTUserSignupTestCase(TestCase):
    URI = '/user/'
    username = 'test'
    payload = {
        'auth_type': 'TEST',
        'username': username,
        'name': 'Test User',
        'email': 'test@example.com',
        'profile_image': 'https://example.com/image',
    }

    username2 = 'test2'
    userprofile2 = {
        'name': 'Normal User',
        'email': 'normal@example.com'
    }

    def setUp(self):
        self.user = UserProfile.create_user(self.username2, self.userprofile2)
        self.token = Token.objects.create(user=self.user).key

    def test_user_signup_required_field(self):
        required_fields = ('auth_type', 'username', 'name', 'email')
        for field in required_fields:
            with self.subTest(missing=field):
                payload = self.payload.copy()
                payload.pop(field)
                response = self.client.post(
                    self.URI,
                    payload,
                    format='json'
                )
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)

    def test_user_signup_non_blank_field(self):
        non_blank_fields = ('auth_type', 'username', 'name', 'email')
        for field in non_blank_fields:
            with self.subTest(blank=field):
                payload = self.payload.copy()
                payload[field] = ''
                response = self.client.post(
                    self.URI,
                    payload,
                    format='json'
                )
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)

    def test_user_signup_success_no_token(self):
        response = self.client.post(
            self.URI,
            self.payload,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertEqual(User.objects.count(), 2)
        user = User.objects.get(username=self.username)
        token = Token.objects.get(user=user).key
        expected_data = {
            'id': user.id,
            'username': self.username,
            'name': self.payload['name'],
            'profile_image': self.payload['profile_image'],
            'token': token
        }
        self.assertEqual(data, expected_data)
        self.assertEqual(user.emails.get().email, self.payload['email'])

    def test_user_signup_success_with_token(self):
        response = self.client.post(
            self.URI,
            self.payload,
            format='json',
            HTTP_AUTHORIZATION=f'Token {self.token}'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertEqual(User.objects.count(), 2)
        user = User.objects.get(username=self.payload['username'])
        token = Token.objects.get(user=user).key
        expected_data = {
            'id': user.id,
            'username': self.payload['username'],
            'name': self.payload['name'],
            'profile_image': self.payload['profile_image'],
            'token': token
        }
        self.assertEqual(data, expected_data)
        self.assertEqual(user.emails.get().email, self.payload['email'])

    def test_user_signup_duplicate_username(self):
        payload = self.payload.copy()
        payload['username'] = self.username2  # duplicate username
        response = self.client.post(
            self.URI,
            payload,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(UserProfile.objects.count(), 1)
        self.assertEqual(EmailAddress.objects.count(), 1)

    def test_user_signup_duplicate_email(self):
        payload = self.payload.copy()
        payload['email'] = self.userprofile2['email']  # duplicate email
        response = self.client.post(
            self.URI,
            payload,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(UserProfile.objects.count(), 1)
        self.assertEqual(EmailAddress.objects.count(), 1)

    def test_user_signup_available_email(self):
        available_email = 'available@example.com'
        email_address = EmailAddress.objects.create(email=available_email)
        assert EmailAddress.objects.count() == 2
        payload = self.payload.copy()
        payload['email'] = available_email
        response = self.client.post(
            self.URI,
            payload,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(EmailAddress.objects.count(), 2)
        user = User.objects.get(username=payload['username'])
        token = Token.objects.get(user=user).key
        expected_data = {
            'id': user.id,
            'username': payload['username'],
            'name': payload['name'],
            'profile_image': payload['profile_image'],
            'token': token
        }
        self.assertEqual(data, expected_data)
        self.assertEqual(user.emails.get().email, available_email)

    def test_user_signup_unavailable_email(self):
        unavailable_email = 'unavailable@example.com'
        EmailAddress.objects.create(email=unavailable_email, user=self.user)
        assert EmailAddress.objects.count() == 2
        payload = self.payload.copy()
        payload['email'] = unavailable_email
        response = self.client.post(
            self.URI,
            payload,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(UserProfile.objects.count(), 1)
        self.assertEqual(EmailAddress.objects.count(), 2)

    def test_user_signup_optional_fields(self):
        optional_fields = ('profile_image',)
        for i, field in enumerate(optional_fields):
            with self.subTest(missing=field):
                payload = self.payload.copy()
                payload['username'] = f'test{i}'
                payload['email'] = f'test{i}@example.com'
                payload.pop(field)
                response = self.client.post(
                    self.URI,
                    payload,
                    format='json'
                )
                self.assertEqual(response.status_code, status.HTTP_201_CREATED)
                data = response.json()
                self.assertEqual(User.objects.count(), 2)
                user = User.objects.get(username=payload['username'])
                token = Token.objects.get(user=user).key
                expected_data = {
                    key: payload.get(key, '') for key in ('username', 'name', 'profile_image')
                }
                expected_data['id'] = user.id
                expected_data['token'] = token
                self.assertEqual(data, expected_data)
                self.assertEqual(user.emails.get().email, payload['email'])
        self.assertEqual(User.objects.count(), 1 + len(optional_fields))

    def test_user_signup_blank_fields(self):
        blank_fields = ('profile_image',)
        for i, field in enumerate(blank_fields):
            with self.subTest(blank=field):
                payload = self.payload.copy()
                payload['username'] = f'test{i}'
                payload['email'] = f'test{i}@example.com'
                payload[field] = ''
                response = self.client.post(
                    self.URI,
                    payload,
                    format='json'
                )
                self.assertEqual(response.status_code, status.HTTP_201_CREATED)
                data = response.json()
                self.assertEqual(User.objects.count(), 2)
                user = User.objects.get(username=payload['username'])
                token = Token.objects.get(user=user).key
                expected_data = {
                    key: payload.get(key, '') for key in ('username', 'name', 'profile_image')
                }
                expected_data['id'] = user.id
                expected_data['token'] = token
                self.assertEqual(data, expected_data)
                self.assertEqual(user.emails.get().email, payload['email'])
        self.assertEqual(User.objects.count(), 1 + len(blank_fields))


class TESTUserLoginTestCase(TestCase):
    URI = '/user/login/'
    auth_type = 'TEST'
    test_username = 'test'
    test_userprofile = {
        'name': 'Test User',
        'profile_image': 'https://example.com/image',
        'email': 'test@example.com',
    }

    username = 'normal'
    userprofile = {
        'name': 'Normal User',
        'email': 'normal@example.com'
    }

    def setUp(self):
        self.test_user = UserProfile.create_user(self.test_username, self.test_userprofile, True)
        self.test_token = Token.objects.create(user=self.test_user).key

        self.user = UserProfile.create_user(self.username, self.userprofile)
        self.token = Token.objects.create(user=self.user).key

    def test_user_login_nonexistent_username(self):
        nonexistent_username = 'nonexistent_username'
        response = self.client.post(
            self.URI,
            {
                'auth_type': self.auth_type,
                'username': nonexistent_username,
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_login_no_username(self):
        response = self.client.post(
            self.URI,
            {
                'auth_type': self.auth_type,
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_login_no_auth_type(self):
        response = self.client.post(
            self.URI,
            {
                'username': self.test_username
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_login_normal_user(self):
        response = self.client.post(
            self.URI,
            {
                'auth_type': self.auth_type,
                'username': self.username
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_login_test_user(self):
        authorities = {
            'no-token': {},  # No token
            'my-token': {'HTTP_AUTHORIZATION': f'Token {self.test_token}'},  # token of user itself
            'other-token': {'HTTP_AUTHORIZATION': f'Token {self.token}'},  # token of other user
        }
        for name, authority in authorities.items():
            with self.subTest(authority=name):
                response = self.client.post(
                    self.URI,
                    {
                        'auth_type': self.auth_type,
                        'username': self.test_username
                    },
                    format='json',
                    **authority
                )
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                data = response.json()
                expected_data = {
                    'id': self.test_user.id,
                    'username': self.test_username,
                    'name': self.test_userprofile['name'],
                    'profile_image': self.test_userprofile['profile_image'],
                    'token': self.test_token,
                }
                self.assertEqual(data, expected_data)


class UserLogoutTestCase(TestCase):
    URI = '/user/logout/'
    username = 'test'
    userprofile = {
        'name': 'Test User',
        'email': 'test@example.com'
    }

    def setUp(self):
        self.user = UserProfile.create_user(self.username, self.userprofile)
        self.token = Token.objects.create(user=self.user).key

    def test_user_logout_without_token(self):
        response = self.client.post(
            self.URI,
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_logout_wrong_token(self):
        invalid_token = 'invalid_token_string'
        response = self.client.post(
            self.URI,
            HTTP_AUTHORIZATION=f'Token {invalid_token}'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_logout_success(self):
        response = self.client.post(
            self.URI,
            HTTP_AUTHORIZATION=f'Token {self.token}'
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.content), 0)
