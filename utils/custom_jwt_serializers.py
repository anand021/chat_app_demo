
from calendar import timegm
from datetime import datetime, timedelta

import jwt
from django.conf import settings
from rest_framework import serializers
from rest_framework_jwt.compat import Serializer as CompactSerializer
from rest_framework_jwt.compat import get_user_model
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.utils import jwt_encode_handler, jwt_payload_handler

from utils.custom_jwt_exceptions import (TokenDecodeException,
                                         TokenExpiredException,
                                         TokenRefreshExpiredException)

User = get_user_model()
jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
jwt_get_username_from_payload = api_settings.JWT_PAYLOAD_GET_USERNAME_HANDLER


class CustomVerificationBaseSerializer(CompactSerializer):
    """
    Abstract serializer used for verifying and refreshing JWTs.
    """
    token = serializers.CharField()

    def validate(self, attrs):
        msg = 'Please define a validate method.'
        raise NotImplementedError(msg)

    def _check_payload(self, token):
        # Check payload valid (based off of JSONWebTokenAuthentication,
        # may want to refactor)
        try:
            payload = jwt_decode_handler(token)
        except jwt.ExpiredSignature:
            raise TokenExpiredException
        except jwt.DecodeError:
            raise TokenDecodeException

        return payload

    def _check_user(self, payload):
        username = jwt_get_username_from_payload(payload)

        if not username:
            msg = _('Invalid payload.')
            raise serializers.ValidationError(msg)
        # Make sure user exists
        try:
            user = User.objects.get_by_natural_key(username)
        except User.DoesNotExist:
            msg = _("User doesn't exist.")
            raise serializers.ValidationError(msg)

        if not user.is_active:
            raise InActiveUserAccountException

        return user


class CustomRefreshJSONWebTokenSerializer(CustomVerificationBaseSerializer):
    """
    Refresh an access token.
    """

    def validate(self, attrs):
        token = attrs['token']

        payload = self._check_payload(token=token)
        user = self._check_user(payload=payload)
        # Get and check 'orig_iat'
        orig_iat = payload.get('orig_iat')

        if orig_iat:
            # Verify expiration
            refresh_limit = settings.JWT_AUTH['JWT_REFRESH_EXPIRATION_DELTA']

            if isinstance(refresh_limit, timedelta):
                refresh_limit = (refresh_limit.days * 24 * 3600 +
                                 refresh_limit.seconds)

            expiration_timestamp = orig_iat + int(refresh_limit)
            now_timestamp = timegm(datetime.utcnow().utctimetuple())
            if now_timestamp > expiration_timestamp:
                raise TokenRefreshExpiredException
        else:
            msg = _('orig_iat field is required.')
            raise serializers.ValidationError(msg)

        new_payload = jwt_payload_handler(user)
        new_token = jwt_encode_handler(new_payload)

        if user.auth_token == token:
            user.secondary_auth_token = new_token
            user.save()
        elif user.secondary_auth_token == token:
            user.auth_token = new_token
            user.save()
        else:
            raise TokenDecodeException

        new_payload['orig_iat'] = orig_iat

        return {
            'token': new_token,
            'user': user
        }
