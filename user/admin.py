from django.contrib import admin

# Register your models here.
from .models import User, UserActivity, UserInfo, UserSettings, UserStatistic, UserSystemInfo

admin.site.register(User)
admin.site.register(UserInfo)
admin.site.register(UserSettings)
admin.site.register(UserActivity)
admin.site.register(UserStatistic)
admin.site.register(UserSystemInfo)