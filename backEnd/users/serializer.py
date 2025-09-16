from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        # Built-in User does not have display_name; use username
        token['display_name'] = getattr(user, 'display_name', None) or user.get_username()
        token['email'] = getattr(user, 'email', '')
        return token