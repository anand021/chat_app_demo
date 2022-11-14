from email import message

from django.conf import settings
from django.contrib.auth import authenticate
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import action, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_jwt.utils import jwt_encode_handler, jwt_payload_handler
from utils import custom_viewsets

from .models import ChatGroups, MessageLikes, Messages
from .serializers import ChatGroupserializer, MessagesSerializer


# Create your views here.
class GroupViewSet(custom_viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    model = ChatGroups
    queryset = ChatGroups.objects.all()
    serializer_class = ChatGroupserializer
    create_success_message = 'Your registration is completed successfully!'
    list_success_message = 'Group list returned successfully!'
    retrieve_success_message = 'Information returned successfully!'
    update_success_message = 'Your information updated successfully!'

    def get_permissions(self):

        if self.action == 'create':
            permission_classes = [IsAuthenticated]
            return [permission() for permission in permission_classes]

        return super().get_permissions()

    
    def perform_create(self, serializer):

        group_object = self.model.objects.create(
            name=self.request.data.get('name').lower())

        
        return group_object
    
    def perform_update(self, serializer):
        instance = self.get_object()

        member_ids = self.request.data.get('members')

        for id in member_ids:
            instance.members.add(id)

        return instance

    @action(detail=False, methods=['POST'])
    def delete_group(self, request):
        group_object = ChatGroups.objects.get(id=request.data.get('id'))
        group_object.is_deleted = True
        group_object.save()

        data = {
            "data": None,
            "message": "delete successful !"
        }

        return Response(data, status=status.HTTP_200_OK)


class MessageViewSet(custom_viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    model = Messages
    queryset = Messages.objects.all()
    serializer_class = MessagesSerializer
    create_success_message = 'Your registration is completed successfully!'
    list_success_message = 'Message list returned successfully!'
    retrieve_success_message = 'Information returned successfully!'
    update_success_message = 'Your information updated successfully!'

    def get_permissions(self):

        if self.action == 'create':
            permission_classes = [IsAuthenticated]
            return [permission() for permission in permission_classes]

        return super().get_permissions()

    
    def create(self, serializer):

        group_obj = ChatGroups.objects.get(id=self.request.data.get('group'))

        msg_object = self.model.objects.create(
            message=self.request.data.get('message').lower(), sender=self.request.user, chat_group=group_obj)

        
        data = {
            "data": None,
            "message": "create successful !"
        }

        return Response(data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['POST'])
    def like_message(self, request):
        if not 'message_id' in request.data:
            data = {
                "data": None,
                "message": "message not found"
            }
            return Response(data, status=status.HTTP_200_OK) 
        
        message_object = Messages.objects.get(id = request.data['message_id'])
        
        MessageLikes.objects.update_or_create(message=message_object, liked_by = request.user)


        data = {
            "data": None,
            "message": "Like successful !"
        }

        return Response(data, status=status.HTTP_200_OK)
