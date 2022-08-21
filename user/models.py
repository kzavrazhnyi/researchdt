from django.db import models

# Create your models here.
import uuid
from typing import Any, Optional

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth.models import Group


class UserManager(BaseUserManager):  # type: ignore
    """UserManager class."""

    # type: ignore
    def create_user(self, email: str, password: Optional[str] = None, is_research = False) -> 'User':
        """Create and return a `User` with an email, username and password."""
    
        if email is None:
            raise TypeError('Users must have an email address.')
       
        user = self.model(email=self.normalize_email(email))
        
        
        user.set_password(password)
        user.save()
        user.set_research_group(is_research)
        return user

    def create_superuser(self, email: str, password: str) -> 'User':  # type: ignore
        """Create and return a `User` with superuser (admin) permissions."""
        if password is None:
            raise TypeError('Superusers must have a password.')

        user = self.create_user(email, password)
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.save()

        return user
    

class User(AbstractBaseUser, PermissionsMixin):
        
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(db_index=True, unique=True)                                 
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    
    class Meta:
        verbose_name = 'Users'
        verbose_name_plural = 'Users'
    # Tells Django that the UserManager class defined above should manage
    # objects of this type.
    objects = UserManager()

    def __str__(self) -> str:
        string = self.email
        return string

    @property
    def tokens(self) -> dict[str, str]:
        refresh = RefreshToken.for_user(self)
        return {'refresh': str(refresh), 'access': str(refresh.access_token)}

    def get_name(self) -> Optional[str]:
        return self.email

    def get_short_name(self) -> str:
        return self.email
    
    def is_research(self) -> bool:
        try:
            return Group.objects.get(name='research').user_set.filter(id=self.id).exists()
        except Group.DoesNotExist:
            return False
        
    def set_research_group(self, is_research) -> str:
        research_group, created = Group.objects.get_or_create(name='research') 
        if is_research:
            research_group.user_set.add(self)
        elif is_research is False and self.is_research():
            research_group.user_set.remove(self)

class UserInfo(models.Model):
    class GenderChoices(models.TextChoices):
        male = 'male'
        female = 'female'
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="info")
    gender = models.CharField(choices=GenderChoices.choices, max_length=6)
    age = models.IntegerField()  
    name = models.CharField(max_length=255)
    subscription = models.CharField(default="", max_length=1000, blank=True)
    device_serial_number = models.CharField(max_length=255, blank=True)
    
    class Meta:
        verbose_name = 'Users Information'
        verbose_name_plural = 'Users Information'
        
    def __str__(self) -> str:
        string = self.user.email
        return string
    
class UserSystemInfo(models.Model):
    class OSChoises(models.TextChoices):
        ios = 'ios'
        android = 'android'
        unknown = 'unknown'
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="system_info")
    os = models.CharField(choices=OSChoises.choices, max_length=7)
    platform_version = models.CharField(max_length=255, blank=True)
    device_model = models.CharField(max_length=255, blank=True)
    manufacturer = models.CharField(max_length=255, blank=True)
    
    class Meta:
        verbose_name = 'Users System Information'
        verbose_name_plural = 'Users System Information'
        
    def __str__(self) -> str:
        string = self.user.email
        return string
    
class UserActivity(models.Model): 
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="activity")
    last_engagement = models.DateTimeField(null=True)

    class Meta:
        verbose_name = 'Users Activity'
        verbose_name_plural = 'Users Activity'
        
    def __str__(self) -> str:
        string = self.user.email
        return string
        
class UserStatistic(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="statistic")
    
    class Meta:
        verbose_name = 'Users Statistic'
        verbose_name_plural = 'Users Statistic'
        
    def __str__(self) -> str:
        string = self.user.email
        return string
    
class UserSettings(models.Model):
    class LocaleChoises(models.TextChoices):
        en = 'en'
        ua = 'ua'
        ru = 'ru'
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="settings")
    locale = models.CharField(choices=LocaleChoises.choices, max_length=255)
    fcm_token = models.CharField(default="", max_length=255, blank=True)
    
    class Meta:
        verbose_name = 'Users Settings'
        verbose_name_plural = 'Users Settings'
        
    def __str__(self) -> str:
        string = self.user.email
        return string
    
