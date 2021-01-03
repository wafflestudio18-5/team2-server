from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from user.models import UserProfile
from rest_framework.authtoken.models import Token


class WadiumSocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        # print(sociallogin)
        # print(data)
        # print(sociallogin.account.extra_data)
        return super(WadiumSocialAccountAdapter, self).populate_user(request, sociallogin, data)

    def save_user(self, request, sociallogin, form=None):
        print(type(sociallogin.account))
        breakpoint()
        userprofile = {
            'email': sociallogin.account.extra_data['email'],
            'name': sociallogin.account.extra_data['name'],
            'profile_image': sociallogin.account.extra_data['picture']
        }
        user = UserProfile.create_user(
            UserProfile.get_unique_username(sociallogin.account.extra_data['email']),
            userprofile)
        Token.objects.create(user=user)
        print(sociallogin.account.provider)
        # TODO create usergoogle, userfacebook
        sociallogin.user = user
        sociallogin.save(request)
        return user
