from django.urls import path
from .views import oauth2_callback, oauth2_login

urlpatterns = [
    path("google/login/", oauth2_login, name='google_no_redirect_login'),
    path("google/login/callback/", oauth2_callback, name='google_no_redirect_callback')
]
