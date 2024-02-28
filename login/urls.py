from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register', views.register_request, name='register'),
    path('reset_password', views.password_reset_request, name='reset'),
    path('login',views.login_request, name='login'),
    path('logout',views.logout_request, name='logout')
]
