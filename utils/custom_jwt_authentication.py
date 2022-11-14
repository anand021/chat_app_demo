import jwt
from rest_framework import exceptions, serializers
from rest_framework.authentication import (BaseAuthentication,
                                           get_authorization_header)
from rest_framework_jwt.compat import get_user_model
from rest_framework_jwt.settings import api_settings

jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
jwt_get_username_from_payload = api_settings.JWT_PAYLOAD_GET_USERNAME_HANDLER


class BaseJSONWebTokenAuthentication(BaseAuthentication):
    """
    Token based authentication using the JSON Web Token standard.
    """

    def authenticate(self, request):
        """
        Returns a two-tuple of `User` and token if a valid signature has been
        supplied using JWT-based authentication.  Otherwise returns `None`.
        """
        jwt_value = self.get_jwt_value(request)
        if jwt_value is None:
            return None
        try:
            payload = jwt_decode_handler(jwt_value)
        except:
            msg = 'Invalid signature.'
            raise exceptions.AuthenticationFailed(msg)
        
        user = self.authenticate_credentials(payload, request)
        print(user)

        return (user, jwt_value.decode())

    def authenticate_credentials(self, payload, request):
        """
        Returns an active user that matches the payload's user id and email.
        """
        User = get_user_model()
        username = jwt_get_username_from_payload(payload)

        authtoken = request.META['HTTP_AUTHORIZATION']
        if 'JWT ' in authtoken:
            self.usertoken = authtoken.split()[1]

        if not username:
            msg = 'Invalid payload.'
            raise exceptions.AuthenticationFailed(msg)

        try:
            user = User.objects.get_by_natural_key(username)
        except User.DoesNotExist:
            msg = 'Invalid signature..'
            raise exceptions.AuthenticationFailed(msg)

        if self.validate_token(user):
            msg = 'Invalid signature...'
            raise exceptions.AuthenticationFailed(msg)

        return user

    def validate_token(self, user):
        return (user.auth_token != self.usertoken)


class JSONWebTokenAuthentication(BaseJSONWebTokenAuthentication):
    """
    Clients should authenticate by passing the token key in the "Authorization"
    HTTP header, prepended with the string specified in the setting
    `JWT_AUTH_HEADER_PREFIX`. For example:
        Authorization: JWT eyJhbGciOiAiSFMyNTYiLCAidHlwIj
    """
    www_authenticate_realm = 'api'

    def get_jwt_value(self, request):
        auth = get_authorization_header(request).split()
        auth_header_prefix = api_settings.JWT_AUTH_HEADER_PREFIX.lower()

        if not auth:
            return None

        if len(auth) == 1:
            msg = 'Invalid Authorization header. No credentials provided.'
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = 'Invalid Authorization header. Credentials string should not contain spaces.'
            raise exceptions.AuthenticationFailed(msg)

        return auth[1]

    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response, or `None` if the
        authentication scheme should return `403 Permission Denied` responses.
        """
        return 'JWT realm="{0}"'.format(self.www_authenticate_realm)


