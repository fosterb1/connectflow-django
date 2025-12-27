from rest_framework import authentication
from rest_framework import exceptions
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate

User = get_user_model()

class FirebaseAuthentication(authentication.BaseAuthentication):
    """
    Scale-Ready Header-based Firebase Authentication.
    Allows Postman/Mobile apps to authenticate using:
    Authorization: Bearer [Firebase_ID_Token]
    """
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header:
            return None

        try:
            # Expected: Bearer <token>
            token = auth_header.split(' ')[1]
        except IndexError:
            raise exceptions.AuthenticationFailed('Invalid token header. No credentials provided.')

        # Use our existing FirebaseBackend logic
        user = authenticate(request, id_token=token)
        
        if not user:
            raise exceptions.AuthenticationFailed('Invalid Firebase Token.')

        return (user, None)
