from base64 import urlsafe_b64encode
from django.shortcuts import get_object_or_404, render

# Create your views here.

from typing import Any, Optional

from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView, CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_bytes

from rest_framework import serializers, exceptions
from user.publisher import publish_email

from user.utils import id_generator
from researchdt.cache import setKey

from .permissions import IsOwnerUserObject
from .models import User
from .serializers import (
    SetNewPasswordByCodeSerializer,
    UserSerializer,
    RetrieveUpdateUserSerializer,
    ResetPasswordEmailRequestSerializer
)
from drf_yasg.utils import swagger_auto_schema
from researchdt.swagger import SwaggerResponses

class RegistrationUserAPIView(CreateAPIView):
    """
    User registartion
    """
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_id='Register user',
        security=[],
        responses={
            201: UserSerializer,
            400: SwaggerResponses.get_validation_error_schema(),
            status.HTTP_500_INTERNAL_SERVER_ERROR: SwaggerResponses.get_common_schema('Internal server error', 500, 'internal_server_error')
        }
    )
    def post(self, request: Request) -> Response:
        """Return user response after a successful registration."""
       
        serializer = self.serializer_class(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
        except serializers.ValidationError as e:
            
            raise serializers.ValidationError(e.args[0])
        
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class RetrieveUpdateUserAPIView(RetrieveUpdateAPIView):
    serializer_class = RetrieveUpdateUserSerializer
    permission_classes = [IsAuthenticated, IsOwnerUserObject]
    
    @swagger_auto_schema(
        operation_id='Get user',
        responses={
            status.HTTP_200_OK: UserSerializer,
            status.HTTP_400_BAD_REQUEST: SwaggerResponses.get_validation_error_schema(),
            status.HTTP_401_UNAUTHORIZED: SwaggerResponses.get_common_schema('Unathorized', 401, 'bad_credentials'),
            status.HTTP_403_FORBIDDEN: SwaggerResponses.get_common_schema('Forbidden', 403, 'permission_denied'),
            status.HTTP_404_NOT_FOUND: SwaggerResponses.get_common_schema('User not found', 404, 'user_not_found'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: SwaggerResponses.get_common_schema('Internal server error', 500, 'internal_server_error')
        }
    )
    def get(self, request: Request, *args: dict[str, Any], **kwargs: dict[str, Any]) -> Response:
        """Return user on GET request."""
         
        try:
             user = User.objects.select_related("info", "system_info", "settings").get(id=kwargs['pk'])
             
        except User.DoesNotExist as e:
            raise exceptions.NotFound('User not found', 'user_not_found')
        
        self.check_object_permissions(self.request, user)
        serializer = self.serializer_class(user, context={'request': request})

        return Response(serializer.data, status=status.HTTP_200_OK)


    @swagger_auto_schema(
        operation_id='Update user',
        responses={
            status.HTTP_200_OK: RetrieveUpdateUserSerializer,
            status.HTTP_400_BAD_REQUEST: SwaggerResponses.get_validation_error_schema(),
            status.HTTP_401_UNAUTHORIZED: SwaggerResponses.get_common_schema('Unathorized', 401, 'bad_credentials'),
            status.HTTP_403_FORBIDDEN: SwaggerResponses.get_common_schema('Forbidden', 403, 'permission_denied'),
            status.HTTP_404_NOT_FOUND: SwaggerResponses.get_common_schema('User not found', 404, 'user_not_found'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: SwaggerResponses.get_common_schema('Internal server error', 500, 'internal_server_error')
        }
    )
    def patch(self, request: Request, *args: dict[str, Any], **kwargs: dict[str, Any]) -> Response:
        """Return updated user."""
        serializer_data = request.data
        try:
             user = User.objects.select_related("info", "system_info", "settings").get(id=kwargs['pk'])
        except User.DoesNotExist as e:
            raise exceptions.NotFound('User not found', 'user_not_found')
        
        self.check_object_permissions(self.request,user)
        
        serializer = self.serializer_class(
            user, data=serializer_data, partial=True, context={'request': request}
        )
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
        except serializers.ValidationError as e:
            raise serializers.ValidationError(e.args[0])
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
       auto_schema=None
    )
    def put(self, request: Request, *args: dict[str, Any], **kwargs: dict[str, Any]) -> Response:
        raise exceptions.MethodNotAllowed("PUT")

class RequestPasswordResetEmail(CreateAPIView):
    serializer_class = ResetPasswordEmailRequestSerializer
    
    @swagger_auto_schema(
        operation_id='Send reset password link',
        security=[],
        responses={
            status.HTTP_200_OK: SwaggerResponses.get_success_schema('Success', 'Successfully sended'),
            status.HTTP_400_BAD_REQUEST: SwaggerResponses.get_validation_error_schema(),
            status.HTTP_500_INTERNAL_SERVER_ERROR: SwaggerResponses.get_common_schema('Internal server error', 500, 'internal_server_error')
        }
    )
    def post(self, request: Request) -> Response:

        email = request.data.get('email', '')
        serializer = self.serializer_class(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            code = id_generator(6)
            if publish_email({'type':'forgot_password_code', 'to':email, 'code': code}) and setKey(email, code, timeout=180):
                dataresponse = 'We have sent you a link to reset your password, key lifetime 180 sec'
                return Response({'success': dataresponse}, status=status.HTTP_200_OK)
            
        except serializers.ValidationError as e:
            raise serializers.ValidationError(e.args[0])
    
class PasswordTokenCheckAPI(CreateAPIView):
    serializer_class = SetNewPasswordByCodeSerializer

    @swagger_auto_schema(
        operation_id='Reset password link',
        security=[],
        responses={
            status.HTTP_200_OK: SwaggerResponses.get_success_schema('Success', 'Done'),
            status.HTTP_400_BAD_REQUEST: SwaggerResponses.get_validation_error_schema(),
            status.HTTP_500_INTERNAL_SERVER_ERROR: SwaggerResponses.get_common_schema('Internal server error', 500, 'internal_server_error')
        }
    )
    def post(self, request: Request, *args, **kwargs) -> Response:

        serializer = self.serializer_class(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
            return Response({'success': 'Done'}, status=status.HTTP_200_OK)
        except serializers.ValidationError as e:
            raise serializers.ValidationError(e.args[0])
        
        
       

          

            
