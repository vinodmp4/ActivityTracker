from django.urls import path

from . import views

urlpatterns = [
    path('admin', views.admin_home, name='admin'),
    path('admin/verify', views.admin_verify, name='admin'),
    path('admin/certificate', views.admin_certificates, name='admin'),
    path('admin/faculty', views.admin_faculty, name='admin'),
    path('admin/otp', views.admin_OTP, name='admin'),
    path('faculty', views.faculty_home, name='faculty'),
    path('faculty/dashboard', views.faculty_dashboard, name='faculty'),
    path('faculty/verify', views.faculty_verify, name='faculty'),
    path('faculty/otp', views.faculty_OTP, name='faculty'),
    path('student', views.student_home, name='student'),
    path('student/notifications', views.student_notifications, name='student'),
    path('student/dashboard', views.student_dashboard, name='student'),
    path('student/newcertificate', views.student_newcertificate, name='student'),
]
