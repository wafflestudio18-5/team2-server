from allauth.account.adapter import DefaultAccountAdapter
from allauth.exceptions import ImmediateHttpResponse
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.http import HttpResponseBadRequest
from rest_framework.authtoken.models import Token
from rest_framework.serializers import ValidationError

from user.models import UserProfile, EmailAddress


class WadiumAccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        return False  # disable account/email signup


class WadiumSocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(self, request, sociallogin):
        return True

    def save_user(self, request, sociallogin, form=None):
        email = sociallogin.account.extra_data['email']
        if sociallogin.account.provider == 'facebook_no_redirect':
            picture = sociallogin.account.extra_data['picture']['data']['url']
        elif sociallogin.account.provider == 'google_no_redirect':
            picture = sociallogin.account.extra_data['picture']
        else:
            picture = ''

        try:
            email_address = EmailAddress.objects.get(email=email)
            if not email_address.available:
                # 해당 이메일로 이미 가입한 유저가 있는지 확인 (이메일 회원가입으로 가입 후 구글 로그인으로 가입하는 경우)
                user = email_address.user
                sociallogin.user = user
                sociallogin.save(request)
                return user
        except EmailAddress.DoesNotExist:
            pass

        userprofile = {
            'email': email,
            'name': sociallogin.account.extra_data['name'],
            'profile_image': picture
        }
        try:
            user = UserProfile.create_user(
                UserProfile.get_unique_username(sociallogin.account.extra_data['email']),
                userprofile)
        except ValidationError as e:
            res = HttpResponseBadRequest(str(e.detail))
            raise ImmediateHttpResponse(res)

        Token.objects.create(user=user)
        sociallogin.user = user
        sociallogin.save(request)
        return user
