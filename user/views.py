from datetime import datetime, timedelta
from sre_constants import SUCCESS

from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.decorators import action, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_jwt.utils import jwt_encode_handler, jwt_payload_handler
from utils import custom_viewsets
from utils.permissions import IsAdminPermission

from user.models import AppUser

from .serializers import AppUserSerializer


class AppUserViewSet(custom_viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    model = AppUser
    queryset = AppUser.objects.all()
    serializer_class = AppUserSerializer
    create_success_message = 'Your registration is completed successfully!'
    list_success_message = 'App Users list returned successfully!'
    retrieve_success_message = 'Information returned successfully!'
    update_success_message = 'Your information updated successfully!'

    def get_permissions(self):

        if self.action in ['login', ]:
            permission_classes = [AllowAny]
            return [permission() for permission in permission_classes]


        if self.action == 'change_password':
            permission_classes = [IsAuthenticated]
            return [permission() for permission in permission_classes]

        if self.action == 'list':
            permission_classes = [IsAuthenticated]
            return [permission() for permission in permission_classes]

        if self.action == 'retrieve':
            permission_classes = [IsAuthenticated]
            return [permission() for permission in permission_classes]

        if self.action in ['create','partial_update', 'update', 'destroy']:
            permission_classes = [IsAuthenticated, IsAdminPermission]
            return [permission() for permission in permission_classes]
        
        # if self.action == 'create':
        #     permission_classes = [AllowAny]
        #     return [permission() for permission in permission_classes]



        return super().get_permissions()

    
    def perform_create(self, serializer):
        if not self.request.data.get('email'):
            data = {"field": "email", "message": "please provide an email"}
            return Response(data,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        user_obj, user_created = self.model.objects.update_or_create(
            email=self.request.data.get('email').lower(), defaults=serializer.validated_data)

        user_obj.set_password(serializer.validated_data.get('password'))
        user_obj.is_active = True
        user_obj.email_verified = True
        user_obj.save()
        return user_obj


    @action(detail=False, methods=['POST'])
    def login(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        data = {
                "data": None,
                "message": 'email and password are required fields'
            }

        if not (email and password):
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        user_obj_query = self.get_queryset().filter(email=email)

        if not user_obj_query.exists():
            data['message'] = "user_does not exist"
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        user_obj = user_obj_query.first()

        if user_obj.is_deleted:
            data['message'] = "user_does is not active"
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        if not user_obj.is_active:
            data['message'] = "user_does is not active"
            return Response(data, status=status.HTTP_400_BAD_REQUEST)


        authenticated_user = authenticate(username=email,
                                          password=password)
        if not authenticated_user:
            data['message'] = "user_does is not active"
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        user_obj = AppUser.objects.get(id=authenticated_user.id)

        payload = jwt_payload_handler(user_obj)
        token = jwt_encode_handler(payload)

        user_obj.auth_token = token
        user_obj.save()

        expiration = datetime.utcnow(
        ) + settings.JWT_AUTH['JWT_EXPIRATION_DELTA']
        expiration_epoch = expiration.timestamp()

        user_obj_serializer = AppUserSerializer(user_obj)

        data = {
            "data": user_obj_serializer.data,
            "token": token,
            "token_expiration": expiration_epoch
        }

        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'])
    def logout(self, request):

        # Invalidating user existing auth token
        request_user = self.request.user
        request_user.auth_token = None
        request_user.save()

        data = {
            "data": None,
            "message": "logout successful !"
        }

        return Response(data, status=status.HTTP_200_OK)
