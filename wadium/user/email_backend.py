from mailjet_rest import Client
from django.conf import settings
from datetime import datetime

mailjet = Client(auth=(settings.MAILJET_API_KEY, settings.MAILJET_API_SECRET), version='v3.1')


def send_access_token(email, signup=False, token=None):
    if signup:
        data = {
            'Messages': [
                {
                    "From": {
                        "Email": "noreply@wadium.shop",
                        "Name": "Wadium"
                    },
                    "To": [
                        {
                            "Email": email,
                            "Name": ""
                        }
                    ],
                    "TemplateID": 2118400,  # 2118400 for signup, 2118280 for signin
                    "TemplateLanguage": True,
                    "Subject": "Finish creating your account on Wadium",
                    "Variables": {
                        "callback_uri": f"https://www.wadium.shop/callback/email?token={token}&operation=register"
                    }
                }
            ]
        }
    else:  # login
        data = {
            'Messages': [
                {
                    "From": {
                        "Email": "noreply@wadium.shop",
                        "Name": "Wadium"
                    },
                    "To": [
                        {
                            "Email": email,
                            "Name": ""
                        }
                    ],
                    "TemplateID": 2118280,  # 2118400 for signup, 2118280 for signin
                    "TemplateLanguage": True,
                    "Subject": "Sign in to Wadium",
                    "Variables": {
                        "callback_uri": f"https://www.wadium.shop/callback/email?token={token}&operation=login"
                    }
                }
            ]
        }
    result = mailjet.send.create(data=data)
    if result.json()['Messages'][0]['Status'] == 'success':
        time = datetime.strptime(result.headers['date'], '%a, %d %b %Y %H:%M:%S %Z')
        return True, time
    else:
        return False, None
