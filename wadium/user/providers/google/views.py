from allauth.socialaccount.providers.google.views import (
    OAuth2CallbackView,
    OAuth2LoginView,
    GoogleOAuth2Adapter,
)
from django.conf import settings
from django.http import HttpResponseRedirect
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from user.serializers import UserSerializer
from .provider import GoogleProviderNoRedirect


class SocialLoginView(APIView):
    def dispatch(self, request, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        request = self.initialize_request(request, *args, **kwargs)
        self.request = request
        self.headers = self.default_response_headers  # deprecate?

        try:
            self.initial(request, *args, **kwargs)
        except Exception as exc:
            pass

    def render(self, response):
        query_string = self.request.META.get('QUERY_STRING')
        if query_string:
            queries = query_string.split('&')
            for i in range(len(queries)):
                if 'state' in queries[i]:
                    queries[i] = 'state=' + 'x' * 12
                elif 'code' in queries[i]:
                    queries[i] = 'code=' + 'x' * 75
            self.request.META['QUERY_STRING'] = '&'.join(queries)
        self.response = self.finalize_response(self.request, response, *self.args, **self.kwargs)
        return self.response


class TokenOAuth2CallbackView(OAuth2CallbackView):
    def dispatch(self, request, *args, **kwargs):
        api_view = SocialLoginView()
        api_view.dispatch(request, *args, **kwargs)
        try:
            res = super(TokenOAuth2CallbackView, self).dispatch(request, *args, **kwargs)
        except:
            res = Response({
                'error': 'An error occurred in social login.',
            }, status=status.HTTP_400_BAD_REQUEST)
            return api_view.render(res)
        if isinstance(res, HttpResponseRedirect) and res.url == settings.LOGIN_REDIRECT_URL:
            assert hasattr(request, 'user')
            # login success
            data = UserSerializer(instance=request.user).data
            token, created = Token.objects.get_or_create(user=request.user)
            data['token'] = token.key
            res = Response(data=data)
        else:
            res = Response({
                'error': 'An error occurred in social login.',
            }, status=status.HTTP_400_BAD_REQUEST)
        return api_view.render(res)


class TokenOAuth2LoginView(OAuth2LoginView):
    def dispatch(self, request, *args, **kwargs):
        api_view = SocialLoginView()
        api_view.dispatch(request, *args, **kwargs)
        res = super(TokenOAuth2LoginView, self).dispatch(request, *args, **kwargs)
        if isinstance(res, HttpResponseRedirect) and res.url:
            url = res.url
            data = {
                'url': url,
            }
            try:
                queries = url.split('?')
                queries = queries[1].split('&')
                for query in queries:
                    if query[:6] == 'state=':
                        data['state'] = query[6:]
            except:
                pass
            if 'state' not in data:
                res = Response({
                    'error': 'An error occurred in social login.'
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                res = Response(data)
        else:
            res = Response({
                'error': 'An error occurred in social login.',
            }, status=status.HTTP_400_BAD_REQUEST)
        return api_view.render(res)


class GoogleOAuth2NoRedirectAdapter(GoogleOAuth2Adapter):
    provider_id = GoogleProviderNoRedirect.id


oauth2_callback = TokenOAuth2CallbackView.adapter_view(GoogleOAuth2NoRedirectAdapter)
oauth2_login = TokenOAuth2LoginView.adapter_view(GoogleOAuth2NoRedirectAdapter)
