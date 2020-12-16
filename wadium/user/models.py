from django.db import models
from django.contrib.auth.models import User
import secrets
from django.utils import timezone


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


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=300)
    profile_image = models.URLField(max_length=300)
    bio = models.CharField(max_length=140)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class UserSocial(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_address = models.OneToOneField(EmailAddress, on_delete=models.CASCADE)
    oauth_token = models.CharField(max_length=100)  # This is unique, but no need to validate.

    class Meta:
        abstract = True


class UserGoogle(UserSocial):
    google_sub = models.CharField(max_length=255, unique=True)


class UserFacebook(UserSocial):
    facebook_id = models.CharField(max_length=100, unique=True)
