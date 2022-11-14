from datetime import datetime, timedelta

from django.contrib.auth import password_validation
from rest_framework import serializers

from .models import AppUser


class DynamicFieldsModelSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class AppUserSerializer(DynamicFieldsModelSerializer):

    class Meta:
        model = AppUser
        exclude = ('is_active','auth_token', 'created_at', 'updated_at')

        read_only_fields = ('id', 'created_at', 'updated_at', 'is_active', 'email')

        extra_kwargs = {
            'password': {'write_only': True,
                         "error_messages": {"required": "Password is mandatory to create your account.."}},
            'email': {"error_messages": {"required": "Email is mandatory to create your account."}}
        }

    def validate_password(self, value):
        password_validation.validate_password(
            password=value, user=self.instance)
        return value
