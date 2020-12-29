from django.db import models, transaction
from django.db.utils import IntegrityError
from django.contrib.auth.models import User
import secrets
from django.utils import timezone
from rest_framework.serializers import ValidationError
from rest_framework.exceptions import AuthenticationFailed
from .email_backend import send_access_token
from rest_framework import status


class EmailAddress(models.Model):
    email = models.EmailField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='emails', null=True)
    primary = models.BooleanField(default=False)  # 이메일 로그인에 사용되는 이메일이 primary 이메일.

    class Meta:
        indexes = [
            models.Index(fields=['user', 'primary'])
        ]

    def __str__(self):
        return self.email

    @property
    def available(self):
        return self.user is None


def generate_token():
    return secrets.token_hex(6)


class EmailAuth(models.Model):
    email_address = models.ForeignKey(EmailAddress, related_name='auths', on_delete=models.CASCADE)
    expires_at = models.DateTimeField(null=True)  # set when email is sent
    valid = models.BooleanField(default=True)

    # 이메일로 전송된 토큰인 경우: True
    # api 요청으로 전송된 토큰인 경우: False
    # signup CHECK 요청은 is_email_token이 True인 경우에만 처리됨.
    is_email_token = models.BooleanField(default=False)

    # May raise IntegrityError when token is not unique for <0.000001 probability.
    token = models.CharField(max_length=12, unique=True, default=generate_token)

    @property
    def expired(self):
        return self.expires_at <= timezone.now()

    def send(self, signup=False):
        sent, at = send_access_token(self.email_address.email, signup, self.token)
        if sent:
            self.is_email_token = True
            self.expires_at = timezone.now() + timezone.timedelta(hours=2)
            self.valid = True
            self.save()
        return sent

    def is_valid(self, must_be_email=True):
        if not self.valid:
            raise AuthenticationFailed({
                'access_token': 'The access token is invalid'
            })
        if must_be_email and not self.is_email_token:
            self.valid = False
            self.save()
            raise AuthenticationFailed({
                'access_token': 'The access token is invalid'
            })
        elif self.expired:
            self.valid = False
            self.save()
            raise AuthenticationFailed({
                'access_token': 'The access token is expired'
            })
        else:  # valid
            self.valid = False  # invalidated when used once
            self.save()
            return True


class UserProfile(models.Model):
    TEST_PW = 'test'
    NORMAL_PW = 'none'
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=300)
    profile_image = models.URLField(max_length=300, blank=True)
    bio = models.CharField(max_length=140, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def email_address(self):
        return self.user.emails.get(primary=True)

    @property
    def email(self):
        return self.user.emails.get(primary=True).email

    @classmethod
    @transaction.atomic
    def create_user(cls, username, userprofile, test_user=False):
        try:
            if test_user:
                user = User.objects.create(username=username, password=cls.TEST_PW)
            else:
                user = User.objects.create(username=username, password=cls.NORMAL_PW)
        except IntegrityError:
            raise ValidationError({'username': 'A user with that username already exists.'})
        userprofile = userprofile.copy()
        email = userprofile.pop('email')
        try:
            email_address = EmailAddress.objects.select_for_update().get(email=email)
        except EmailAddress.DoesNotExist:
            try:
                email_address = EmailAddress.objects.create(email=email, user=user, primary=True)
            except IntegrityError:
                raise ValidationError({'email': 'A user with that email already exists.'})
        else:
            if email_address.available:
                email_address.user = user
                email_address.primary = True
                email_address.save()
            else:
                raise ValidationError({'email': 'A user with that email already exists.'})
        cls.objects.create(user=user, **userprofile)
        return user

    @classmethod
    def get_unique_username(cls, email):
        basename = email[:email.index('@')]
        similar_names = {u.username for u in User.objects.filter(username__startswith=basename)}
        if basename not in similar_names:
            return basename
        postfixes = {n[len(basename):] for n in similar_names}
        for postfix in map(str, range(len(postfixes) + 1)):
            if postfix not in postfixes:
                return basename + postfix


class UserSocial(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_address = models.OneToOneField(EmailAddress, on_delete=models.CASCADE)
    oauth_token = models.CharField(max_length=100, blank=True)  # This is unique, but no need to validate.

    class Meta:
        abstract = True


class UserGoogle(UserSocial):
    google_sub = models.CharField(max_length=255, unique=True)


class UserFacebook(UserSocial):
    facebook_id = models.CharField(max_length=100, unique=True)
