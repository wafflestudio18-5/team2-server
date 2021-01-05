from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from user.models import UserProfile, EmailAddress
from rest_framework.authtoken.models import Token
from rest_framework.serializers import ValidationError
from allauth.exceptions import ImmediateHttpResponse
from django.http import HttpResponseBadRequest
from user.serializers import *

class WadiumAccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        return False  # disable account/email signup


class WadiumSocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(self, request, sociallogin):
        return True

    def save_user(self, request, sociallogin, form=None):
        email = sociallogin.account.extra_data['email']
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

        if sociallogin.account.provider == 'google':
            userprofile = {
                'email': email,
                'name': sociallogin.account.extra_data['name'],
                'profile_image': sociallogin.account.extra_data['picture']
            }

        elif sociallogin.account.provider == "facebook":
            userprofile = {
                'email': email,
                'name': sociallogin.account.extra_data['name'],
                'profile_image': sociallogin.account.extra_data['picture']['data']['url']
            }

        try:
            user = UserProfile.create_user(
                UserProfile.get_unique_username(sociallogin.account.extra_data['email']), userprofile)
        except ValidationError as e:
            res = HttpResponseBadRequest(str(e.detail))
            raise ImmediateHttpResponse(res)

        Token.objects.create(user=user)
        # print(sociallogin.account.provider)
        # TODO create usergoogle(id, email_address, ...), userfacebook(id)
        # TODO usergoogle은 처음에 인증 정보를 저장하기 위해 만든 model인데, allauth를 사용하면서 필요가 없어졌습니다.
        # TODO connections 확인 용도 외에는 필요가 없어서 usergoogle이나 userfacebook 구현은 미뤄도 될 것 같습니다.
        sociallogin.user = user
        sociallogin.save(request)
        return user
