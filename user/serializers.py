from email.policy import default
from django.conf import settings

from rest_framework import exceptions, serializers
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.contrib.auth.password_validation import validate_password

from researchdt.cache import deleteKey, getKey
from .models import User, UserActivity, UserInfo, UserSettings, UserStatistic, UserSystemInfo
from .utils import validate_email as email_is_valid

from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.db import transaction
from django.db.models import Prefetch

class UserInfoSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=255, required=True)
    age = serializers.IntegerField(required=True)
    gender = serializers.ChoiceField(choices=UserInfo.GenderChoices, required=True)
    subscription = serializers.CharField(default="", max_length=1000, required=False)
    device_serial_number = serializers.CharField(default="", max_length=1000, required=False)
    class Meta:
        fields = ( 'name', 'age', 'gender', 'subscription', 'device_serial_number')
        model = UserInfo
        
        
class UserSettingsSerializer(serializers.ModelSerializer):
    locale = serializers.ChoiceField(choices=UserSettings.LocaleChoises, required=True)
    fcm_token = serializers.CharField(default="", max_length=255,required=False)
    class Meta:
        fields = ['locale', 'fcm_token']
        model = UserSettings
        
class UserSystemInfoSerializer(serializers.ModelSerializer):
    os = serializers.ChoiceField(choices=UserSystemInfo.OSChoises, required=True)
    platform_version = serializers.CharField(default="", max_length=255, required=False)
    device_model = serializers.CharField(default="", max_length=255, required=False)
    manufacturer = serializers.CharField(default="", max_length=255, required=False)
    
    class Meta:
        fields = ['os', 'platform_version', 'device_model', 'manufacturer']
        model = UserSystemInfo
        
class UserSerializer(serializers.ModelSerializer):
    """Handle serialization and deserialization of User objects."""

    info=UserInfoSerializer(required=True)
    settings=UserSettingsSerializer(required=True)
    system_info=UserSystemInfoSerializer(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    is_research = serializers.BooleanField(required=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'info', 'settings', 'is_research', 'system_info', 'tokens']

    def validate_email(self, value):
        lower_email = value.lower()
        if User.objects.filter(email__iexact=lower_email).exists():
            raise serializers.ValidationError("Email is exist")
        return lower_email

    
    def create(self, validated_data):
        """Return user after creation."""
        #try:
        with transaction.atomic():
            user = User.objects.create_user(
                email=validated_data['email'], 
                password=validated_data['password'],
                is_research=validated_data['is_research']
            )
            
            info_data=validated_data.pop('info')
            settings_data=validated_data.pop('settings')
            system_info_data=validated_data.pop('system_info')
            
            UserInfo.objects.create(user=user, **info_data) 
            UserSettings.objects.create(user=user, **settings_data)
            UserSystemInfo.objects.create(user=user, **system_info_data)
            UserActivity.objects.create(user=user)
            UserStatistic.objects.create(user=user)
            return user 

class RetrieveUpdateUserSerializer(serializers.ModelSerializer):
    """Handle serialization and deserialization of User objects."""

    info=UserInfoSerializer(required=False)
    settings=UserSettingsSerializer(required=False)
    system_info=UserSystemInfoSerializer(required=False)
    email = serializers.EmailField(required=False)
    is_research = serializers.BooleanField(required=False)
    
    password = serializers.CharField(write_only=True, required=False, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=False)
    old_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['id', 'email', 'is_research', 'info', 'settings', 'system_info', 'groups', 'old_password', 'password', 'password2']
    
    def validate(self, attrs):
        
        password = attrs.get("password",None)
        password2 = attrs.get("password2",None)
        old_password = attrs.get("old_password",None)
        if password is not None and password2 is None:
           raise serializers.ValidationError({"password2": "A password2 is required."}, code="required")
        elif password is not None and old_password is None:
            raise serializers.ValidationError({"old_password": "Old password is required."}, code="required")
        elif password is not None and password != password2:
            raise serializers.ValidationError({"password": "Password fields didn't match."}, code="invalid")

        return attrs

    def validate_email(self, value):
        user = self.instance
        lower_email = value.lower()
        if user.email == lower_email:
            return lower_email
        if User.objects.filter(email__iexact=lower_email).exists():
            raise serializers.ValidationError("Email is exist", "email_exist")
        return lower_email
    
    def validate_old_password(self, value):
        user = self.instance
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is not correct", "old_password_incorrect")
        return value

    def update(self, user, validated_data):  # type: ignore
        """Perform an update on a User."""
        with transaction.atomic():
            password = validated_data.pop('password', None)
            info_data=validated_data.pop('info', None)
            settings_data=validated_data.pop('settings', None)
            system_info_data=validated_data.pop('system_info', None)
            is_research = validated_data.pop('is_research', None)
               
            if info_data is not None:
                for (key, value) in info_data.items():
                    setattr(user.info, key, value)
                user.info.save()
                
                
            if settings_data is not None:
                for (key, value) in settings_data.items(): 
                    setattr(user.settings, key, value)
                user.settings.save()
               
                
            if system_info_data is not None:
                for (key, value) in system_info_data.items():
                    setattr(user.system_info, key, value)
                user.system_info.save()
                
            for (key, value) in validated_data.items():
                setattr(user, key, value)

            if is_research is not None:
                user.set_research_group(is_research)
                
            if password is not None:
                user.set_password(password)

            user.save()
            return user
    
class ResetPasswordEmailRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    class Meta:
        fields = ['email']
        
    def validate_email(self, value: str) -> str:
        """Normalize and validate email address."""
        valid, error_text = email_is_valid(value)
        if not valid:
            raise serializers.ValidationError(error_text)
        try:
            email_name, domain_part = value.strip().rsplit('@', 1)
        except ValueError:
            pass
        else:
            value = '@'.join([email_name, domain_part.lower()])

        lower_email = value.lower()
        if not User.objects.filter(email=lower_email).exists():
            raise serializers.ValidationError('User not found by email.', 'email_is_not_exist')
        
        return value
    
 
    
class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        min_length=6,  required=True, max_length=68, write_only=True)
    uidb64 = serializers.CharField(write_only=True, required=True)
    token = serializers.CharField(write_only=True, required=True)

    class Meta:
        fields = ['password','uidb64','token']

    def validate(self, attrs):
        try:
     
            password = attrs.get('password')
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')

            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise serializers.ValidationError('The reset data is invalid', 'reset_data_invalid')

            user.set_password(password)
            user.save()

            return (user)
        except Exception as e:
            raise serializers.ValidationError('The reset data is invalid', 'reset_data_invalid')
        
class SetNewPasswordByCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, write_only=True)
    password = serializers.CharField(
        min_length=6,  required=True, max_length=68, write_only=True)
    code = serializers.CharField(min_length=6, max_length=6, required=True, write_only=True)
    
    class Meta:
        fields = ['password','code']

    def validate(self, attrs):
        try:
            email = attrs.get('email')
            password = attrs.get('password')
            code = attrs.get('code')
            
            try:
                user = User.objects.get(email=email)
                print(user)
            except User.DoesNotExist:
                raise User.DoesNotExist
            
            if getKey(email) != code:
                raise serializers.ValidationError('The reset data is invalid', 'reset_data_invalid')
            deleteKey(email)
            user.set_password(password)
            user.save()

            return (user)
        except Exception as e:
            raise serializers.ValidationError('The reset data is invalid', 'reset_data_invalid')
        