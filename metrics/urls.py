from django.urls import path

from . import views

urlpatterns = [
    path('', views.site_metrics, name='metrics'),
]
