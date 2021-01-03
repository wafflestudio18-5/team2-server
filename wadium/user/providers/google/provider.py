from allauth.socialaccount.providers.google.provider import GoogleProvider


class GoogleProviderNoRedirect(GoogleProvider):
    id = 'google_no_redirect'
    name = 'Custom Google'


provider_classes = [GoogleProviderNoRedirect]
