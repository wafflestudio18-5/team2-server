from django.urls import path
from .views import oauth2_callback, oauth2_login
from .provider import FacebookProviderNoRedirect
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

urlpatterns = [
    path("facebook/login/", oauth2_login, name='facebook_no_redirect_login'),
    path("facebook/login/callback/", oauth2_callback, name='facebook_no_redirect_callback')
]