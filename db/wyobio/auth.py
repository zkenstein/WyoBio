from django.contrib.auth.backends import ModelBackend
from django.conf import settings
from django.contrib.auth.models import User

import requests

class Backend(ModelBackend):
    def authenticate(self, username=None, password=None, **kwargs):
    
        response = requests.post(settings.AUTH_CHECK_URL, {
            'username': username,
            'password': password,
        })

        uid = int(response.text)
        if uid:
            user, is_new = User.objects.get_or_create(
                id=uid,
                username=username
            )
            return user
        else:
            return None
