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

        data = response.json()
        if data:
            # Search for or create user with matching id
            user, is_new = User.objects.get_or_create(
                id=data['uID'],
                username=username
            )
            # Copy additional fields
            user.is_active = (data['uIsActive'] == "1")
            user.save()
            
            if not user.is_active:
                return None
            return user
        else:
            return None
