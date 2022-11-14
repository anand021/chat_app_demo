from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import AppUserViewSet

app_name = 'app_user'

router = DefaultRouter(trailing_slash=False)

router.register('app_users', AppUserViewSet)

urlpatterns = [

    *router.urls
]
