from django.contrib import admin
from .models import certificate_type, certificate


# Register your models here.
admin.site.register(certificate_type)
admin.site.register(certificate)
