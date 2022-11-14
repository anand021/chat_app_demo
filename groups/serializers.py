from datetime import datetime, timedelta

from django.contrib.auth import password_validation
from rest_framework import serializers

from .models import ChatGroups, Messages


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


class ChatGroupserializer(DynamicFieldsModelSerializer):

    class Meta:
        model = ChatGroups
        exclude = ('created_at', 'updated_at')

        read_only_fields = ('id', 'created_at', 'updated_at')



class MessagesSerializer(DynamicFieldsModelSerializer):

    class Meta:
        model = Messages
        exclude = ('created_at', 'updated_at')

        read_only_fields = ('id', 'created_at', 'updated_at')
