import requests
from allauth.socialaccount import providers
from allauth.socialaccount.providers.facebook.provider import GRAPH_API_URL
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.facebook.views import compute_appsecret_proof

from .provider import FacebookProviderNoRedirect
from ..google.views import TokenOAuth2LoginView, TokenOAuth2CallbackView


def fb_complete_login(request, app, token):
    provider = providers.registry.by_id(FacebookProviderNoRedirect.id, request)
    resp = requests.get(
        GRAPH_API_URL + "/me",
        params={
            "fields": ",".join(provider.get_fields()),
            "access_token": token.token,
            "appsecret_proof": compute_appsecret_proof(app, token),
        },
    )
    resp.raise_for_status()
    extra_data = resp.json()
    login = provider.sociallogin_from_response(request, extra_data)
    return login


class FacebookOAuth2NoRedirectAdapter(FacebookOAuth2Adapter):
    provider_id = FacebookProviderNoRedirect.id

    def complete_login(self, request, app, access_token, **kwargs):
        return fb_complete_login(request, app, access_token)

    def get_callback_url(self, request, app):
        base_url = request.META.get('HTTP_ORIGIN', '')
        if base_url not in (
                'https://wadium.shop',
                'https://www.wadium.shop',
        ):
            return super(FacebookOAuth2NoRedirectAdapter, self).get_callback_url(request, app)
        callback_url = base_url + '/callback/facebook/'
        return callback_url


oauth2_callback = TokenOAuth2CallbackView.adapter_view(FacebookOAuth2NoRedirectAdapter)
oauth2_login = TokenOAuth2LoginView.adapter_view(FacebookOAuth2NoRedirectAdapter)
