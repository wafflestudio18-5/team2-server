from allauth.socialaccount.providers.facebook.provider import FacebookProvider


class FacebookProviderNoRedirect(FacebookProvider):
    id = 'facebook_no_redirect'
    name = 'Custom Facebook'


provider_classes = [FacebookProviderNoRedirect]