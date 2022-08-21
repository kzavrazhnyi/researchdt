from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    LoginAPIView,
    DecoratedTokenRefreshView
)

#app_name = 'user'

urlpatterns = [
    path('/login', LoginAPIView.as_view(), name='login_user'),
    path('/refresh', DecoratedTokenRefreshView.as_view(), name='token_refresh'),
]