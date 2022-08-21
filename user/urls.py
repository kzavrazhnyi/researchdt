from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    PasswordTokenCheckAPI,
    RegistrationUserAPIView,
    RequestPasswordResetEmail,
    RetrieveUpdateUserAPIView
)

#app_name = 'user'

urlpatterns = [
    #path('0/', RegistrationAPIView.as_view(), name='register_user'),
    path('', RegistrationUserAPIView.as_view(), name='get_user'),
    path('/<uuid:pk>', RetrieveUpdateUserAPIView.as_view(), name='retrieve_update_user'),
    path('/forgot-password', RequestPasswordResetEmail.as_view(), name='forgot_password'),
    path('/forgot-password/set', PasswordTokenCheckAPI.as_view(), name='forgot_password_confirm'),
]