from django.contrib import admin
from .models import Profile, OTP, Notification

# Register your models here.
admin.site.register(Profile)
admin.site.register(OTP)
admin.site.register(Notification)
