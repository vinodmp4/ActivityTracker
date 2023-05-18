from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fullname = models.CharField(max_length=50,default="Unknown User")
    regid = models.CharField(max_length=15,default="NA")
    acayear = models.IntegerField(default=1990)
    dept = models.CharField(max_length=50,default="select")
    email = models.CharField(max_length=50,default="NA")
    mobno = models.CharField(max_length=10,default="NA")
    usertype = models.CharField(max_length=2,default="st")
    verified =  models.BooleanField(default=False)
    verify_applied = models.BooleanField(default=False)
    mentor = models.IntegerField(default=-1)

    def __str__(self):
        return f'{self.user.username}'

# Create your models here.
