from allauth.socialaccount.helpers import complete_social_login
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
            if "error" in request.GET or "code" not in request.GET:
                # Distinguish cancel from error
                res = Response({
                    'error': 'An error occurred in social login.',
                }, status=status.HTTP_400_BAD_REQUEST)
                return api_view.render(res)
            app = self.adapter.get_provider().get_app(self.request)
            client = self.get_client(self.request, app)

            try:
                access_token = self.adapter.get_access_token_data(request, app, client)
                token = self.adapter.parse_token(access_token)
                token.app = app
                login = self.adapter.complete_login(
                    request, app, token, response=access_token
                )
                login.token = token
                # if self.adapter.supports_state:
                #     login.state = SocialLogin.verify_and_unstash_state(
                #         request, get_request_param(request, "state")
                #     )
                # else:
                #     login.state = SocialLogin.unstash_state(request)

            res = complete_social_login(request, login)
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

    def get_callback_url(self, request, app):
        base_url = request.META.get('HTTP_ORIGIN', '')
        if base_url not in (
                'http://localhost:3000',
                'https://wadium.shop',
                'https://www.wadium.shop',
        ):
            return super(GoogleOAuth2NoRedirectAdapter, self).get_callback_url(request, app)
        callback_url = base_url + '/callback/google/'
        return callback_url


oauth2_callback = TokenOAuth2CallbackView.adapter_view(GoogleOAuth2NoRedirectAdapter)
oauth2_login = TokenOAuth2LoginView.adapter_view(GoogleOAuth2NoRedirectAdapter)
