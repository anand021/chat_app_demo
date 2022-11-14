from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import GroupViewSet, MessageViewSet

app_name = 'groups'

router = DefaultRouter(trailing_slash=False)

router.register('app_groups', GroupViewSet)
router.register('messages', MessageViewSet)

urlpatterns = [

    *router.urls
]
