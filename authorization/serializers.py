
from user.models import User
from rest_framework import exceptions, serializers
from django.contrib.auth import authenticate
from user.serializers import UserInfoSerializer, UserSettingsSerializer
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
    
class LoginSerializer(serializers.ModelSerializer):
    email = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=128, write_only=True)
    info = UserInfoSerializer(read_only=True)
    settings = UserSettingsSerializer(read_only=True)
    is_research = serializers.BooleanField(read_only=True)
    tokens = serializers.SerializerMethodField()

    def get_tokens(self, obj):  
        user = User.objects.get(email=obj.email)

        return {'refresh': user.tokens['refresh'], 'access': user.tokens['access']}

    class Meta:
        model = User
        fields = ['id', 'email', 'is_research' ,'password', 'info', 'settings', 'tokens']
        

    def validate(self, data): 
        email = data.get('email', None)
        password = data.get('password', None)

        user = authenticate(username=email, password=password)
        
        if user is None:
            raise exceptions.AuthenticationFailed()

        return user
    
class TokenRefreshResponseSerializer(serializers.Serializer):
    access = serializers.CharField()

    def create(self, validated_data):
        raise NotImplementedError()

    def update(self, instance, validated_data):
        raise NotImplementedError()
    
    
class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):  # type: ignore
        """Validate token."""
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):  # type: ignore
        """Validate save backlisted token."""

        try:
            RefreshToken(self.token).blacklist()
        except TokenError as ex:
            raise exceptions.AuthenticationFailed(ex)