from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status, exceptions, serializers
from rest_framework.permissions import AllowAny

from rest_framework.generics import CreateAPIView

from authorization.exceptions import InvalidCredentials

from .serializers import LoginSerializer, TokenRefreshResponseSerializer
from drf_yasg.utils import swagger_auto_schema
from rest_framework_simplejwt.views import (
    TokenRefreshView
)
from researchdt.swagger import SwaggerResponses


class LoginAPIView(CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    @swagger_auto_schema(
        operation_id='Login user',
        security=[],
        responses={
            status.HTTP_200_OK: LoginSerializer,
            status.HTTP_400_BAD_REQUEST: SwaggerResponses.get_validation_error_schema(),
            status.HTTP_401_UNAUTHORIZED: SwaggerResponses.get_common_schema('Unathorized', 401, 'bad_credentials'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: SwaggerResponses.get_common_schema('Internal server error', 500, 'internal_server_error')
        }
    )
    def post(self, request: Request) -> Response:
        """Return user after login."""
        
        user = request.data

        serializer = self.serializer_class(data=user)
        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError as e:
            raise serializers.ValidationError(e.args[0])
        except exceptions.AuthenticationFailed:
            raise InvalidCredentials


        return Response(serializer.data, status=status.HTTP_200_OK)
    
class DecoratedTokenRefreshView(TokenRefreshView):
    @swagger_auto_schema(
        operation_id='Refresh token',
        security=[],
        responses={
            status.HTTP_201_CREATED: TokenRefreshResponseSerializer,
            status.HTTP_400_BAD_REQUEST: SwaggerResponses.get_validation_error_schema(),
            status.HTTP_401_UNAUTHORIZED: SwaggerResponses.get_common_schema('Unathorized', 401, 'token_not_valid'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: SwaggerResponses.get_common_schema('Internal server error', 500, 'internal_server_error')
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)