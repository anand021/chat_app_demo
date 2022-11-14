from datetime import datetime

from django.db.models import Q
from django.utils import timezone
from rest_framework import permissions

CUSTOM_MESSAGE = "You don't have permission to do this action!"


class IsAdminPermission(permissions.BasePermission):
    message = CUSTOM_MESSAGE

    def has_permission(self, request, view):
        user_obj = request.user
        if user_obj.is_admin and user_obj.is_active and user_obj.auth_token:
            return True
